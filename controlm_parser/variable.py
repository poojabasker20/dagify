class Variable():
    name = None
    value = None
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def set_name(self, name):
        self.name = name
        
    def setValue(self, value):
        self.value = value
        
    def get_name(self):
        return self.name
    
    def getValue(self):
        return self.value
        
    

        
        
   
