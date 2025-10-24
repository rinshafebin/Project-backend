class CasesOnlyRouter:

    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'cases':
            return True
        return False