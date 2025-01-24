from FractalEngine import *
MyNodes={"A":RegularPolyDesc(7,referenceangle=pi/7),
         "B":RegularPolyDesc(4,referenceangle=pi/4),
         "C":RegularPolyDesc(3,referenceangle=pi/3)}


for i in range(0,1000):
    t=i/1000
    cpath={"length":2+abs(cos(t*tau*2)),"scaling":0.6+sin(t*tau)*0.08,"key":"C"}
    myrules={"A":[None,cpath,None,cpath,None,None],
                  "B":[{"length":1.25+abs(sin(t*tau*2)),"scaling":0.6+sin(t*tau*5)*.1,"key":"A"},{"length":1.5+cos(t*tau*2)*.7,"scaling":0.8,"key":"B"},{"length":1.5,"scaling":0.7+sin(t*pi*5)*.4,"key":"C"}],
                  "C":[{"length":2+abs(cos(t*tau*3)),"scaling":1.05-cos(t*tau*5)*.1,"key":"A"},{"length":3+abs(sin(t*tau*3)),"scaling":0.75,"key":"B"}]}
    F=Fractal(Nodes=MyNodes,StartNode="A",Rules=myrules,Branch={"length":3+sin(t*tau),"scaling":.8,"key":"A"})
    im=F.Make(scale=75,depth=13,origin=(middle[0]-75,middle[1]))
    im.save("Frames/%04d.png"%i)
