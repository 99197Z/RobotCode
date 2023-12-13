import uuid
class DataPoint:
    def __init__(self,f,*a) -> None:
        self.f = f
        self.a = a
    def __call__(self):
        return self.f(*self.a)
class Logger:
    def __init__(self,items) -> None:
        self.items = items
        self.data = ""
        self.line(items.keys())
        
    def line(self,items):
        line = ''
        for i in items:
            line += str(i) + ","
        self.data += line.removesuffix(',') + "\n"
    def __call__(self):
        data = []
        for k,v in self.items.items():
            data.append(v())
        self.line(data)
    def save(self):
        print(self.data)

log = Logger({
    "test":DataPoint(uuid.uuid4),
    "tst":DataPoint(uuid.uuid4)
})
log()
log()
log.save()