from PIL import Image,ImageDraw
from math import cos,sin,pi,sqrt,atan2,e


########CONSTANTS VARIABLES FUNCTIONS ##########
Res=1080*2,1080*2
middle=Res[0]//2,Res[1]//2
tau=pi*2
hp=pi*.5
def dist(A,B):
    return sqrt(sum(map(lambda l,r:(r-l)**2,A,B)))
    
def midangle(a,b,r):
    if b<a and a<tau:
        b=b+tau
    return a+(b-a)*r
        
def midpoint(a,b,r=0.5):
    return list(map(lambda lft,rght:lft+(rght-lft)*r,a,b))

def anglefrom(A,B):
    return atan2(B[1]-A[1],B[0]-A[0])

def rotatearound(Point,Pole,Radians):
    c1=(Point[0]+Point[1]*1j)
    c2=(Pole[0]+Pole[1]*1j)
    result=(c1-c2)*e**(1j*Radians)+c2
    return (result.real,result.imag)

################CLASS DEFINITIONS ##############



class NodeDesc:
    def __init__(self,vertices,inp,outp,set_states={},delete_states={},change_states={},referenceangle=0):
        self.inp=inp
        self.angles=[inp[2]-referenceangle]+[o[2]-referenceangle for o in outp]
        self.outp=outp
        self.referenceangle=referenceangle
        self.states={"Set":set_states,"Del":delete_states,"Change":change_states}
        self.vertices=vertices
    def preview(self,scale=200,res=(600,600),origin=(0,0)):
        origin=origin[0]+res[0]//2,origin[1]+res[1]//2
        im=Image.new("RGB",res,(0,0,0))
        dr=ImageDraw.Draw(im)
        Transform=lambda v:(int(origin[0]+v[0]*scale),int(origin[1]+v[1]*scale))
        truepoints=map(Transform,self.vertices)
        dr.polygon(list(truepoints),fill=(255,255,255)) ## Draw Main Shape
        for i in self.outp:
            dr.line((Transform(i[0]),Transform(i[1])),fill=(0,100,200),width=10) ### Draw output Sides
        dr.line((Transform(self.inp[0]),Transform(self.inp[1])),fill=(200,30,20),width=10) ##Draw Input Side
        im.save("preview.png")

def RegularPolyDesc(sides,states={"Set":{},"Del":{},"Change":{}},referenceangle=0):
    points=[(round(cos(side/sides*tau),13),round(sin(side/sides*tau),13)) for side in range(sides+1)]
    pointdist=dist(points[0],points[1])
    points=[(p[0]/pointdist,p[1]/pointdist) for p in points]
    inp=(points[0],points[1],anglefrom((0,0),midpoint(points[0],points[1])))
    outp=[(points[n],points[n+1],anglefrom((0,0),midpoint(points[n],points[n+1]))) for n in range(1,sides)]
    
    return NodeDesc(points,inp,outp,referenceangle=referenceangle)

Square=RegularPolyDesc(4,referenceangle=pi/4)

Square.preview()


################CLASS DEFINITIONS ##############

class CenteredNode:
    def __init__(self,desc,origin,angle=hp,scale=200):
        self.desc=desc
        self.angles=[a+angle for a in self.desc.angles]##Already Translated
        self.translation=lambda point:rotatearound((origin[0]+point[0]*scale,origin[1]+point[1]*scale),origin,angle-desc.referenceangle) #function
        self.inp=(self.translation(desc.inp[0]),self.translation(desc.inp[1]))
        self.outp=[(self.translation(o[0]),self.translation(o[1])) for o in desc.outp]
        self.vertices=[self.inp[0]]+[i[0] for i in self.outp]
    def draw(self,scale,res,origin,col=(255,255,255)):
        origin=origin[0]+res[0]//2,origin[1]+res[1]//2
        return (self.vertices,col) ## Draw Main Shape
        

def ChildNode(desc,origin,angle=hp,scale=200):
    CenterPosition=midpoint(origin[0],origin[1])
    midpoint(desc.inp[0],desc.inp[1])
    CenterPosition[0]=CenterPosition[0]+cos(angle)*scale*0.3
    CenterPosition[1]=CenterPosition[1]+sin(angle)*scale*0.3
    node=CenteredNode(desc,CenterPosition,angle+pi,scale)
    return node,CenterPosition
        
        

class Connector:
    def __init__(self,origin,angle,scale,length,scaling):
        self.origin=origin #2 points
        self.angle=angle
        self.scale=scale
        self.length=length
        self.scaling=scaling
        self.endscale=scale*scaling
        self.truelength=scale*length
        self.destination=[(o[0]+cos(angle)*self.truelength,o[1]+sin(angle)*self.truelength) for o in self.origin]
        #extrude origin into destination.
        destinationcenter=midpoint(self.destination[0],self.destination[1])
        ##pinch origin points together or spread apart based on scaling
        self.destination[0]=midpoint(destinationcenter,self.destination[0],scaling)
        self.destination[1]=midpoint(destinationcenter,self.destination[1],scaling)
        self.vertices=[(int(a[0]),int(a[1])) for a in [origin[0],self.destination[0],self.destination[1],origin[1]]]
    def draw(self,col=(200,220,255)):
        return (self.vertices,col)
        

##RULES
###{KEY:[branch1,branch2,branch3]}
MyBranch={"length":1,"scaling":0.5,"key":"A"}
DefaultRules={"A":[MyBranch]*3}

class Fractal:
    def __init__(self,Nodes={"A":Square},StartNode="A",Branch=None,StartAngle=0,Rules=DefaultRules):
        self.Nodes=Nodes
        self.StartNode=StartNode
        self.Branch=Branch
        self.StartAngle=StartAngle
        self.Rules=Rules
        
    def Make(self,scale=100,origin=middle,depth=6):
        self.ToDraw=[]
        for i in range(depth+1):
            self.ToDraw.append([])##Create a list of things to draw later.
        #each layer is stored in its own list so the order its drawn can be altered (reversed)
        TopNode=CenteredNode(self.Nodes[self.StartNode],origin,self.StartAngle,scale)
        bgcol=(0,0,0)
        im=Image.new("RGB",Res,bgcol)
        dr=ImageDraw.Draw(im)
        ####Draw TopNode
        self.ToDraw[depth].append(TopNode.draw(scale,Res,origin,col=(80,depth*20,80)))

        ##If specified make a branch on the input since topnode has no parent node occupying its input
        if self.Branch:
            self.MakeBranch(TopNode.inp,TopNode.angles[0],scale,self.Branch,depth-1)
        #Make Child Branches on output
        n=0
        for i in TopNode.outp:
            if self.Rules[self.StartNode][n]!=None:
                self.MakeBranch(i,TopNode.angles[n+1],scale,self.Rules[self.StartNode][n],depth-1)
            n+=1
                

        for layers in self.ToDraw:
            for instructions in layers:
                dr.polygon(instructions[0],fill=instructions[1])
        return im
    def MakeBranch(self,parentorigin,angle,scale,branch,depth):
        if depth>0:
            Conn=Connector(parentorigin,angle,scale,branch["length"],branch["scaling"])
            
            ##Draw Connector
            self.ToDraw[depth].append(Conn.draw(col=(depth*20,40,depth*10)))
            ##Draw Child
            Node,nodeorigin=ChildNode(self.Nodes[branch["key"]],Conn.destination,angle,Conn.endscale)
            self.ToDraw[depth].append(Node.draw(Conn.endscale,Res,nodeorigin,col=(80,depth*20,80)))
            ##Make Child Branches (repeat this function until depth is 0 (or less somehow)
            n=0
            for i in Node.outp:
                if self.Rules[branch["key"]][n]!=None:
                    self.MakeBranch(i,Node.angles[n+1],Conn.endscale,self.Rules[branch["key"]][n],depth-1)
                n+=1
        else:
            return 0 ###DONE!

#f=Fractal(Branch={"length":2,"scaling":1,"key":"A"})

def makeimage(filename,fractalargs):
    #f=Fractal(*fractalargs)
    f=Fractal(Branch=None)

    im=f.Make(depth=14,scale=280)
    im.save(filename)
fps=30
def monocell_videoloop(Branchfunc,filename,length=fps*36,Nodes={"A":Square},depth=36,scale=180):
    for frame in range(0,length):
        t=frame/fps
        FrameRules={"A":Branchfunc(t)}
        f=Fractal(Branch=None,Rules=FrameRules,Nodes=Nodes)

        im=f.Make(depth=depth,scale=scale,origin=(middle[0]+200,middle[1]+200))
        im.save(filename%frame)
        del f
        del im
if __name__=='__main__':
    monocell_videoloop(lambda time:[{"length":sin(time/36*2*tau+1)*.5+0.51,"scaling":0.35+cos(time/36*tau)*.15,"key":"A"},
                                    {"length":abs(cos(time/36*3*tau+2))*-.8+1,"scaling":0.4+cos(time/36*tau)*.25,"key":"A"},
                                    {"length":sin(time/36*3*tau+3)*.5+0.8,"scaling":0.5-abs(sin(time/36*pi))*.45,"key":"A"}],
                       "Frames/frame%04d.png")

