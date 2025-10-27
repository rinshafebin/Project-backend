from functools import partial
from time import timezone
from urllib import request, response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from advocates.models import Case, CaseDocument, CaseNote,AdvocateTeam
from django.shortcuts import get_object_or_404
from advocates.permissions import IsAdvocate
from django.contrib.auth import get_user_model
from django.db.models import Q
from advocates.serializers import (
    AdvocateTeamSerializer, 
    AdvocateTeamCreateSerializer,
    CaseDocumentSerializer,
    CaseNoteSerializer,
    CaseSerializer,
    )


User = get_user_model()

# ------------------ Advocate APIs --------------------

class AdvocateTeamListCreateView(APIView):
    permission_classes = [IsAuthenticated,IsAdvocate]
    
    def get(self,request):
        teams=AdvocateTeam.objects.filter(lead=request.user)
        serializer = AdvocateTeamSerializer(teams,many=True)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    def post(self,request):
        serilaizer = AdvocateTeamCreateSerializer(data= request.data)
        if serilaizer.is_valid():
            serilaizer.save(lead=request.user)
            return Response(serilaizer.data, status=status.HTTP_201_CREATED)
        return Response(serilaizer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdvocateTeamDetailView(APIView):
    permission_classes=[IsAuthenticated,IsAdvocate]
    
    def get_object(self,pk,user):
        try:
            return AdvocateTeam.objects.get(pk=pk,lead=user)
        except AdvocateTeam.DoesNotExist:
            return None
        
    def get(self,request,pk):
        team =self.get_object(pk,request.user)
        if not team:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
  
        serializer = AdvocateTeamSerializer(team)
        return Response(serializer.data)
    
    def put(self,request,pk):
        team = self.get_object(pk,request.user)
        if not team:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdvocateTeamCreateSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        team = self.get_object(pk,request.user)
        if not team:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AdvocateTeamMemberView(APIView):
    def post(self,request,pk):
        member_id = request.data.get(pk=pk,lead=request.user)
        try:
            team = AdvocateTeam.objects.get(pk=pk,lead=request.user)
            member = User.objects.get(id=member_id)
            team.members.add(member)
            return Response({"message": f"{member.username} added to team."}, status=status.HTTP_200_OK)
        except(AdvocateTeam.DoesNotExist,User.DoesNotExist):
            return Response({"error": "Invalid team or member"}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request,pk):
        member_id = request.data.get('member_id')
        try:
            team = AdvocateTeam.objects.get(pk=pk,lead=request.user)
            member = User.objects.get(id=member_id)
            team.members.remove(member)
            return Response({"message": f"{member.username} removed from team."}, status=status.HTTP_200_OK)
          
        except (AdvocateTeam.DoesNotExist, User.DoesNotExist):
            return Response({"error": "Invalid team or member"}, status=status.HTTP_400_BAD_REQUEST)
     


class AdvocateDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        advocate = request.user
        cases = Case.objects.filter(advocate=advocate)

        # --- Case counts ---
        total_cases = cases.count()
        active_cases = cases.filter(status='Active').count()
        completed_cases = cases.filter(status='Closed').count()

        # --- Result-based stats ---
        won_cases = cases.filter(result='Won').count()
        lost_cases = cases.filter(result='Lost').count()
        total_decided_cases = won_cases + lost_cases
        win_rate = (won_cases / total_decided_cases * 100) if total_decided_cases > 0 else 0

        # --- Client count ---
        total_clients = cases.values('client').distinct().count()

        # --- Upcoming hearings ---
        today = timezone.now().date()
        upcoming_hearings = (
            cases.filter(hearing_date__gte=today)
            .order_by('hearing_date')
            .values('title', 'hearing_date', 'status')
        )

        return Response({
            "total_cases": total_cases,
            "active_cases": active_cases,
            "completed_cases": completed_cases,
            "won_cases": won_cases,
            "lost_cases": lost_cases,
            "win_rate": round(win_rate, 2),
            "total_clients": total_clients,
            "upcoming_hearings": list(upcoming_hearings),
        })
        
# ------------------ CaseManagement APIs --------------------

class CaseListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        user =request.user
        query = request.GET.get('q','').strip()
        cases = Case.objects.filter(Q(advocate=user)|Q(team_members=user)).distinct()
        if query:
            cases = Case.objects.filter(
                Q(title__icontains=query)|
                Q(client__username__icontains=query)|
                Q(documents__document__icontains=query)|
                Q(notes__note__icontains=query)    
            ).distinct()
            
        serializer = CaseSerializer(cases, many=True)
        return Response({
            "success": True,
            "message": f"Found {len(serializer.data)} case(s)",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(advocate=request.user)  
            return Response({
                "success": True,
                "message": "Case created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Case creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        

class CaseDetailView(APIView):
    permission_classes = [IsAuthenticated,IsAdvocate]
    
    def get_object(self,pk,user):
        try:
            return Case.objects.get(Q(pk=pk),Q(advocate=user)|Q(team_members=user))  
        except Case.DoesNotExist:
            return None
        
    def get(self,request,pk):
        case = self.get_object(pk,request.user)
        if not case:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CaseSerializer(case)
        return Response(serializer.data)
    
    def put(self,request,pk):
        case = self.get_object(pk,request.user)
        if not case:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CaseSerializer(case,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self,request,pk):        
        case = self.get_object(pk,request.user)
        if not case:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        case.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CaseAddTeamMemberView(APIView):    
    def post(self,request,pk):
        try:
            case=Case.objects.get(pk=pk,advocate=request.user)
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
            case.team_members.add(user)
            return Response({"message": f"{user.username} added to case."}, status=status.HTTP_200_OK)
        except (Case.DoesNotExist, User.DoesNotExist):
            return Response({"error": "Invalid case or user"}, status=status.HTTP_400_BAD_REQUEST)
                





# ------------------ Case DOCUMENTS  View --------------------

class CaseDocumentView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request, case_id):
        documents = CaseDocument.objects.filter(case_id=case_id)
        serializer = CaseDocumentSerializer(documents, many=True)
        return Response({
            "success": True,
            "message": f"Found {len(serializer.data)} document(s)",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, case_id):
        case = get_object_or_404(Case, pk=case_id)
        serializer = CaseDocumentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(case=case)
            return Response({
                "success": True,
                "message": "Document uploaded successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Document upload failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CaseNotesView(APIView):
    permission_classes = [IsAuthenticated,IsAdvocate]
    
    def get(self,request,case_id):
        notes =CaseNote.objects.filter(case_id=case_id)
        serializer = CaseNoteSerializer(notes,many=True)
        return Response(serializer.data)
    
    def post(self,request,case_id):
        try:
            case=Case.objects.get(pk=case_id)
            serializer = CaseNoteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(case=case, created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Case.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

