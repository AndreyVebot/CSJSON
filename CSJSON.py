import json

class CSJSON(dict):
    """
    Class for store JSON, safety update in Firebase or DynamoDB and acces with .dot notation

    Attributes
    ---------------------
    [Key] - return specitied Key
    UpdateMask : dict
        Updated fields as JSON
    UpdateMask2FB : dict
        dot separated JSON for sending into Firebase
    JSON : dict
        current JSON object

    Methods:
    ---------------------
    SafeUpdate(JSON : map, Dotted : bool = False)
        Safety update JSON (prevent deletion of usually presented data)
    DotUpdate(Key : str, Value)
        Update single JSON value. Key value is dot separated like first.second.third
    """

    __JSON__ : None  # Current JSON
    __USON__ : None  # Update JSON (plain)
    __PLAIN__ : None # Current plain struecture

    def JSON2Plain(self, Source : dict) -> dict:
        """
        Convert source JSON into plain notation. Inside plain notation contain full JSON path but each level as array element
        """
        Result = {}
        for Key in Source:
            if type(Source[Key]) == dict:
                Cache = self.JSON2Plain(Source[Key])
                for Key2 in Cache:
                    Result[json.dumps([Key] + [json.loads(Key2)], ensure_ascii = False)] = Cache[Key2]
            if type(Source[Key]) != dict:
                Result[json.dumps(Key, ensure_ascii = False)] = Source[Key]
        return(Result)

    def __init__(self, JSON : map = {}):
        super().__init__(JSON)
#        self.__JSON__ = JSON
        self.__USON__ = {}
        self.__PLAIN__ = {}
        return

    def __DecodePath(self, Key : str) -> list:
        """
        Decode path into list
        Key may be:
            dot-separated path like 'Parent.Child'
            or json.loads path like '["Parent", "Child"]'
            or tuple like ("Parent", "Child")
        """
        if type(Key) == tuple or type(Key) == list: Key = json.dumps(Key)
        if type(Key) != str:
            raise TypeError('Only string as key!')
        try:
            return(json.loads(Key))
        except: pass
        if Key.find('.') > 0 and Key.find('"') < 0 and Key.find("'") < 0: # Try dot-separated path
            return(Key.split('.'))
        return([Key]) # Return simple key

    def __dict__(self):
        return(dict(self))

    def __getitem__(self, Key : str):
        """
        Key may be:
            dot-separated path like 'Parent.Child'
            or json.loads path like '["Parent", "Child"]'
            or tuple like ("Parent", "Child")
        if no node found - return None
        """
#        if self.__JSON__ == None: self.__JSON__ = {}
        if Key in self: return(dict(self)[Key])  # If key in JSON - return this simple result

        try: # May be Key if CSJSON compatible path
            FullPath = self.__DecodePath(Key)
            def GetByPath(JSON : dict, Path : list):
                if len(Path) == 1:
                    return(JSON[Path[0]])
                return(GetByPath(JSON[Path[0]],Path[1:]))

            if FullPath == 1:
                return(super().__getitem__(FullPath[0]))
            return(GetByPath(super().__getitem__(FullPath[0]),FullPath[1:]))
#            return(GetByPath(self.JSON,FullPath))
        except: 
            return None


    def __setitem__(self, Key, Value):
        """
        Key may be:
            dot-separated path like 'Parent.Child'
            or json.loads path like '["Parent", "Child"]'
            or tuple like ("Parent", "Child")
        if no node found - return None
        """
        def SetByPath(JSON : dict, Path : list, Value):
            if not Path[0] in JSON: 
                if len(Path) == 1: 
                    JSON[Path[0]] = Value # Set value
                    return
                else: 
                    JSON[Path[0]] = {}  # Create node
            if len(Path) == 1:
                JSON[Path[0]] = Value
                return
            return(SetByPath(JSON[Path[0]], Path[1:], Value))


        FullPath = self.__DecodePath(Key)
        if len(FullPath) == 1:
            super().__setitem__(FullPath[0],Value) 
        else:
            if not FullPath[0] in self: super().__setitem__(FullPath[0],{}) 
            SetByPath(super().__getitem__(FullPath[0]),FullPath[1:], Value)
        SetByPath(self.__USON__,FullPath, Value)
        self.__PLAIN__[json.dumps(FullPath)] = Value   # Mark for plain data update
        return

#    @property
#    def JSON(self) -> map:
#        return self.__JSON__

    @property
    def Plain(self) -> map:
        if self.__PLAIN__ == None: self.__PLAIN__ = self.JSON2Plain(dict(self))
        return self.__PLAIN__

    @property
    def UpdateMask(self) -> map:        
        return self.__USON__

    @property
    def UpdateMask2FB(self) -> map:
        """
        Firebase document update mask (dot - separated)
        """
        ParRes = {}
        for Key in self.JSON2Plain(self.UpdateMask):
            ParRes['.'.join(json.loads(Key))] = self[Key]
        return(ParRes)


DA = {"k" : {"l" : 12}}
DA = {"a" : {"c" : DA, "d" : ["zzz","fff"]}}

Test = CSJSON(DA)
Test.SafeUpdate({"a": {"m" : 1}})
Test.SafeUpdate({"x": {"m" : 1}})
Test.DotUpdate('k.l', 11)
print(Test.UpdateMask2FB)
Test['12']['325435'] = 12
print(Test.Plain)
