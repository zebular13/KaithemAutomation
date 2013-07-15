import weakref,threading,time,os,random,workers,json
from collections import defaultdict


_subscribers_list_modify_lock = threading.Lock()

tester = {}
def test():
    FAIL = False
    def dostuff():
        def dummy(a,b):
            pass
        time.sleep(random.random()/100)
        subscribe('a',dummy)
        postMessage('a','poopoo')
        del dummy
    
    def datatest():
        i = str(os.urandom(10)).replace('/','|')
        def recive(x,y):
            tester[x] = y
        
        subscribe(i,recive)
        x =str(os.urandom(100))
        postMessage(i,x)
        time.sleep((random.random()/100)+0.05)
        if not tester[i] == x:
            FAIL = True
        else:
            #print("hooray")
            pass
            
    def datatest2():
        i = 'potty/'+str(os.urandom(10)).replace('/','|')
        def recive(x,y):
            tester[x] = y
        
        subscribe('potty/',recive)
        x =str(os.urandom(100))
        postMessage(i,x)
        time.sleep((random.random()/100)+0.05)
        if not tester[i] == x:
            FAIL = True
        else:
            #print("hooray")
            pass
    
    for i in range(0,1):
        for i in range(0,100):
            t = threading.Thread(target=dostuff)
            t.start()
            t = threading.Thread(target=datatest)
            t.start()
            t = threading.Thread(target=datatest2)
            t.start()
            time.sleep(0.05)    
    return (not FAIL) and (len(__bus.subscribers.keys())<5)
    
        
    
    


class MessageBus(object):
    
    def __init__(self,executor = None):
        """You pass this a function of one argument that just calls its argument. Defaults to calling in
        same thread and ignoring errors.
        """
        if executor==None:
            def do(self, f):
                try:
                    f()
                except:
                    pass
            self.executor = do
        else:
            self.executor = executor
            
        self.subscribers = defaultdict(list)
        
    def subscribe(self,topic,callback):
        if topic.startswith('/'):
            if not len(topic)==1:
                topic = topic[1:]
        #Allright, here is how this works.
        #We have to deal with the possibility that, at any time,
        #The callback will cease to exist. That, in fact, is how one unsubscribes.
        #So, we make this here closure that knows the topic, and
        #When the GC goes Om Nom Nom on the function, we get passed the weakref to it.
        #Then we get rid of the empty weakref and if that causes the entire topic
        #To have no subscribers, delete that too in case of memory leak.
        def delsubscription(weakrefobject):
            try:
                self.subscribers[topic].remove(weakrefobject)
            except:
                pass
            #There is a very slight chance someone will
            #Add something to topic before we delete it but after the test.
            #That would result in a canceled subscription
            #So we use this lock.
            with _subscribers_list_modify_lock:
                if not self.subscribers[topic]:
                    self.subscribers.pop(topic)
        
        self.subscribers[topic].append(weakref.ref(callback,delsubscription))
    
    
    def parseTopic(self,topic ):
        "Parse the topic string into a list of all subscriptions that could possibly match."
        if topic.startswith('/'):
            topic = topic[1:]
        #A topic foo/bar/baz would go to
        #foo, foo/bar, and /foo/bar/baz
        #So we need to make a list like that
        matchingtopics = set(['/'])
        parts = topic.split("/")
        last = ""
        matchingtopics.add(topic)
        for i in parts:
            last += (i+'/')
            matchingtopics.add(last)
        return matchingtopics
    
    def _post(self, topic,message):
        matchingtopics = self.parseTopic(topic)
        
        #We can't iterate on anything that could possibly change so we make copies
        d = self.subscribers.copy()
        for i in matchingtopics:
            if i in d:
                #When we find a match, we make a copy of that subscriber list
                x = list(d[i])
                #And iterate the copy
                for ref in x:
                    #we call the ref to get its refferent
                    #An error could happen in the subscriber
                    #Or a typeerror could because the weakref has been collected
                    #We ignore both of these errors and move on
                    try:
                        f =ref()(topic,message)
                    except:
                        pass
                    
    
    def postMessage(self, topic, message):
        #Use the executor to run the post message job
        #To allow for the possibility of it running in the background as a thread
        
        #A little more checking than usual here because the message bus is so central.
        #Also, if anyone implements logging they will appreciate no crap on the bus.
        
        try:
            topic = str(topic)
        except Exception:
            raise TypeError("Topic must be a string or castable to a string.")
        
        #Ugly way to find if json serializable. Just try it
        try:
            json.dumps(message)
        except Exception:
            raise ValueError("Message must be serializable as JSON")
        
        def f():
            self._post(topic,message)
        self.executor(f)
        
        
        

__bus = MessageBus(workers.do)      
subscribe = __bus.subscribe
postMessage = __bus.postMessage
        
    
        
    

