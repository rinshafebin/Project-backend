# advocates/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import AdvocateProfile, AdvocateTeam, User, Specialization
from .serializers import (
    AdvocateProfileSerializer,
    AdvocateTeamSerializer,
    AdvocateTeamCreateSerializer,
    SpecializationSerializer
)
from .permissions import IsAdvocate
from django.shortcuts import get_object_or_404


class AdvocateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        """
        Get the current advocate's profile.
        """
        user = request.user
        profile = get_object_or_404(AdvocateProfile, user=user)
        serializer = AdvocateProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update advocate profile.
        """
        user = request.user
        profile = get_object_or_404(AdvocateProfile, user=user)
        serializer = AdvocateProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpecializationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        List all specializations.
        """
        specs = Specialization.objects.all()
        serializer = SpecializationSerializer(specs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new specialization.
        """
        serializer = SpecializationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdvocateTeamListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get(self, request):
        """
        List teams created by this advocate (lead).
        """
        user = request.user
        teams = AdvocateTeam.objects.filter(lead=user)
        serializer = AdvocateTeamSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new team (lead = current user).
        Accepts: { "member_ids": [1,2,3] }
        """
        data = request.data.copy()
        data["lead"] = request.user.id  # assign team lead

        serializer = AdvocateTeamCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save(lead=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdvocateTeamDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdvocate]

    def get_team(self, user, pk):
        """
        Only return a team if the current user is the team lead.
        """
        return get_object_or_404(AdvocateTeam, id=pk, lead=user)

    def get(self, request, pk):
        """
        Retrieve a team by ID (only if user is team lead).
        """
        team = self.get_team(request.user, pk)
        serializer = AdvocateTeamSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update team members.
        Body can include:
           { "member_ids": [1,2,3] }
        """
        team = self.get_team(request.user, pk)

        serializer = AdvocateTeamCreateSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(lead=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete the team.
        """
        team = self.get_team(request.user, pk)
        team.delete()
        return Response({"message": "Team deleted successfully"}, status=status.HTTP_204_NO_CONTENT)





# class AdvocateDashboardView(APIView):
#     permission_classes = [IsAuthenticated, IsAdvocate]

#     def get(self, request):
#         advocate = request.user
#         cases = Case.objects.filter(advocate=advocate)

#         # --- Case counts ---
#         total_cases = cases.count()
#         active_cases = cases.filter(status='Active').count()
#         completed_cases = cases.filter(status='Closed').count()

#         # --- Result-based stats ---
#         won_cases = cases.filter(result='Won').count()
#         lost_cases = cases.filter(result='Lost').count()
#         total_decided_cases = won_cases + lost_cases
#         win_rate = (won_cases / total_decided_cases * 100) if total_decided_cases > 0 else 0

#         # --- Client count ---
#         total_clients = cases.values('client').distinct().count()

#         # --- Upcoming hearings ---
#         today = timezone.now().date()
#         upcoming_hearings = (
#             cases.filter(hearing_date__gte=today)
#             .order_by('hearing_date')
#             .values('title', 'hearing_date', 'status')
#         )

#         return Response({
#             "total_cases": total_cases,
#             "active_cases": active_cases,
#             "completed_cases": completed_cases,
#             "won_cases": won_cases,
#             "lost_cases": lost_cases,
#             "win_rate": round(win_rate, 2),
#             "total_clients": total_clients,
#             "upcoming_hearings": list(upcoming_hearings),
#         })
        
# # ------------------ CaseManagement APIs --------------------

# class CaseListCreateView(APIView):
#     permission_classes = [IsAuthenticated, IsAdvocate]

#     def get(self, request):
#         user =request.user
#         query = request.GET.get('q','').strip()
#         cases = Case.objects.filter(Q(advocate=user)|Q(team_members=user)).distinct()
#         if query:
#             cases = Case.objects.filter(
#                 Q(title__icontains=query)|
#                 Q(client__username__icontains=query)|
#                 Q(documents__document__icontains=query)|
#                 Q(notes__note__icontains=query)    
#             ).distinct()
            
#         serializer = CaseSerializer(cases, many=True)
#         return Response({
#             "success": True,
#             "message": f"Found {len(serializer.data)} case(s)",
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = CaseSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(advocate=request.user)  
#             return Response({
#                 "success": True,
#                 "message": "Case created successfully",
#                 "data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "success": False,
#             "message": "Case creation failed",
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)
        

# class CaseDetailView(APIView):
#     permission_classes = [IsAuthenticated,IsAdvocate]
    
#     def get_object(self,pk,user):
#         try:
#             return Case.objects.get(Q(pk=pk),Q(advocate=user)|Q(team_members=user))  
#         except Case.DoesNotExist:
#             return None
        
#     def get(self,request,pk):
#         case = self.get_object(pk,request.user)
#         if not case:
#             return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = CaseSerializer(case)
#         return Response(serializer.data)
    
#     def put(self,request,pk):
#         case = self.get_object(pk,request.user)
#         if not case:
#             return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = CaseSerializer(case,data=request.data,partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
#     def delete(self,request,pk):        
#         case = self.get_object(pk,request.user)
#         if not case:
#             return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
#         case.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class CaseAddTeamMemberView(APIView):    
#     def post(self,request,pk):
#         try:
#             case=Case.objects.get(pk=pk,advocate=request.user)
#             user_id = request.data.get('user_id')
#             user = User.objects.get(id=user_id)
#             case.team_members.add(user)
#             return Response({"message": f"{user.username} added to case."}, status=status.HTTP_200_OK)
#         except (Case.DoesNotExist, User.DoesNotExist):
#             return Response({"error": "Invalid case or user"}, status=status.HTTP_400_BAD_REQUEST)
                





# # ------------------ Case DOCUMENTS  View --------------------

# class CaseDocumentView(APIView):
#     permission_classes = [IsAuthenticated, IsAdvocate]

#     def get(self, request, case_id):
#         documents = CaseDocument.objects.filter(case_id=case_id)
#         serializer = CaseDocumentSerializer(documents, many=True)
#         return Response({
#             "success": True,
#             "message": f"Found {len(serializer.data)} document(s)",
#             "data": serializer.data
#         }, status=status.HTTP_200_OK)

#     def post(self, request, case_id):
#         case = get_object_or_404(Case, pk=case_id)
#         serializer = CaseDocumentSerializer(data=request.data)

#         if serializer.is_valid():
#             serializer.save(case=case)
#             return Response({
#                 "success": True,
#                 "message": "Document uploaded successfully",
#                 "data": serializer.data
#             }, status=status.HTTP_201_CREATED)

#         return Response({
#             "success": False,
#             "message": "Document upload failed",
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


# class CaseNotesView(APIView):
#     permission_classes = [IsAuthenticated,IsAdvocate]
    
#     def get(self,request,case_id):
#         notes =CaseNote.objects.filter(case_id=case_id)
#         serializer = CaseNoteSerializer(notes,many=True)
#         return Response(serializer.data)
    
#     def post(self,request,case_id):
#         try:
#             case=Case.objects.get(pk=case_id)
#             serializer = CaseNoteSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(case=case, created_by=request.user)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Case.DoesNotExist:
#             return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)

