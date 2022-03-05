import json


class PlainJSON:
    __JSON__ : None  # Current JSON
    __USON__ : None  # Update JSON (plain)
    __PLAIN__ : None # Current plain struecture

    def JSON2Plain(self, Source : dict) -> dict:
        Result = {}
        for Key in Source:
            if type(Source[Key]) == dict:
                Cache = self.JSON2Plain(Source[Key])
                for Key2 in Cache:
                    Result[json.dumps([Key] + json.loads(Key2), ensure_ascii = False)] = Cache[Key2]
            if type(Source[Key]) != dict:
                Result[json.dumps([Key], ensure_ascii = False)] = Source[Key]
        return(Result)

    def __UpdateJSON__(self, PlainKey : str, Value, JSON : dict = None):
        """
        Update JSON by full path
        """
        if JSON == None: JSON = self.__JSON__
        KeyPath = json.loads(PlainKey)
        if len(KeyPath) > 1:
            if not KeyPath[0] in JSON: JSON[KeyPath[0]] = {}
            self.__UpdateJSON__(json.dumps(KeyPath[1:]), Value, JSON = JSON[KeyPath[0]])
            return
        JSON[KeyPath[0]] = Value
        return


    def __init__(self, JSON : map):
        self.__JSON__ = JSON
        self.__USON__ = {}
        self.__PLAIN__ = None
        return

    def __getitem__(self, Key):
        if self.__JSON__ == None: self.__JSON__ = {}
        if not Key in self.__JSON__: self.__JSON__[Key] = {}
        return self.__JSON__[Key]

    def __setitem__(self, Key, Value):
        if not Key in self.Plain:
            self.__PLAIN__[Key] = None
        if self.__PLAIN__[Key] != Value:
            self.__USON__[Key] = Value
        self.__PLAIN__[Key] = Value
        self.__UpdateJSON__(Key,Value)
        return

    @property
    def JSON(self) -> map:
        return self.__JSON__

    @property
    def Plain(self) -> map:
        if self.__PLAIN__ == None: self.__PLAIN__ = self.JSON2Plain(self.__JSON__)
        return self.__PLAIN__


    def SafeUpdate(self, JSON : map, Dotted : bool = False):
        """
        Safe update internal JSON (prevent from reqriting nodes) + generate UpdateMask
        """
        PlainData = {}
        if Dotted:
            for Field in JSON:
                NewKey = Field.split('.')
                PlainData[json.dumps(NewKey, ensure_ascii = False)] = JSON[Field]
        if not Dotted: 
            PlainData = self.JSON2Plain(JSON)

        for Field in PlainData:
            self[Field] = PlainData[Field]
        return


    def DotUpdate(self, Key : str, Value):
        """
        Update single value
        """
        self.SafeUpdate({Key: Value}, Dotted=True)
        return

    @property
    def UpdateMask(self) -> map:
        return self.__USON__

    @property
    def UpdateMask2FB(self) -> map:
        """
        Firebase document update mask (dot - separated)
        """
        ParRes = {}
        for Key in self.UpdateMask:
            ParRes['.'.join(json.loads(Key))] = self.UpdateMask[Key]
        return(ParRes)


DA = {"k" : {"l" : 12}}
DA = {"a" : {"c" : DA, "d" : ["zzz","fff"]}}

Test = PlainJSON(DA)
Test.SafeUpdate({"a": {"m" : 1}})
Test.SafeUpdate({"x": {"m" : 1}})
Test.DotUpdate('k.l', 11)
print(Test.UpdateMask2FB)
Test['12']['325435'] = 12
print(Test.Plain)
