from FractalEngine import *
MyNodes={"A":RegularPolyDesc(7,referenceangle=pi/7)}

monocell_videoloop(lambda time:[None,
    {"length":cos(time/36*2*tau+1)*.4+0.74,"scaling":0.5+sin(time/36*2*tau)*.20,"key":"A"},
                                None,
                                {"length":abs(cos(time/36*3*tau+2))*-.4+1.1,"scaling":0.5+cos(time/36*tau)*.20,"key":"A"},
                                None,
                                {"length":sin(time/36*3*tau+3)*.4+0.9,"scaling":0.7-abs(sin(time/36*pi))*.25,"key":"A"}],"Frames2/A%04d.png",length=36*30,Nodes=MyNodes,depth=10,scale=220)

