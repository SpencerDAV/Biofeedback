from kivy.app import App
from kivy.clock import Clock
from functools import partial
import os, random
from operator import itemgetter

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.splitter import Splitter
from kivy.uix.relativelayout import RelativeLayout
from kivy.garden.graph import Graph, MeshLinePlot
from DemoMetrics import ReadData, RRMetrics
from kivy.properties import *
import serial

#from kivy.graphics.vertex_instructions import (Rectangle,Ellipse,Line)


Builder.load_string('''
#:kivy 1.6



<FeedbackBarWidget>:
    id: barmain
    colour: 0,1,0
    slider: slider_id
    
    #current: (root.current if hasattr(root,"current") else 0)
    #threshhold: (root.threshhold if hasattr(root, "threshhold") else 0.5)
    
    #graf_on:
    orientation: 'horizontal'
    
    Slider:
        id: slider_id
        value_normalized: barmain.threshhold
        
        orientation: 'vertical'
        size_hint: 0.3, 1
        step: 1 
        on_touch_move:
            barmain.threshhold = self.value_normalized


    BoxLayout:        
        id: bar
        orientation:'vertical'
        BoxLayout:    
            padding: 10,10,10,10
            id: base
            orientation: 'vertical'

            canvas.after:
                Color:
                    rgb: (1,1,1)
                Rectangle:
                    size: self.size
                    pos: self.pos
                Color:
                    rgb: (barmain.r,barmain.g,barmain.b)
                Rectangle:
                    id: level
                    pos: self.pos
                    size: self.size[0], self.size[1] * (barmain.current - barmain.minimum)/max(1,(barmain.maximum-barmain.minimum))
                Color:
                    rgb: 2,0,0
                Rectangle:
                    id: threshhold
                    pos: self.pos[0] , self.pos[1] + self.size[1]*(barmain.threshhold) - self.size[1]/100
                    size: self.size[0], self.size[1]/50
    
    
        Label:
            text: barmain.id
            size_hint: 1 , 0.05
        BoxLayout:
            id: textboxs
            orientation: 'vertical'
            size_hint: 1 , 0.3
            BoxLayout:
                id: cv
                size_hint: 1 , 0.1
                orientation: 'horizontal'
                Label:
                    text:'Current:'
                    font_size: self.width/4
                TextInput:
                    id: value
                    multiline: False
                    text: str('%.2f' % barmain.current)
                    font_size: self.width/3.5
                    on_text_validate:                   
                        root.current = float(self.text)
                        self.text = str(root.current)


            BoxLayout:
                size_hint: 1 , 0.1
                orientation: 'horizontal'
                Label:
                    text:"Max:"
                    font_size: self.width/3.5
                TextInput:
                    multiline: False
                    text: str('%.2f' % barmain.maximum)
                    font_size: self.width/3.5
                    on_text_validate:
                        root.rescale_thresh('maximum',float(self.text))
                        root.maximum = float(self.text)
                        self.text = str(root.maximum)
            BoxLayout:
                size_hint: 1 , 0.1
                orientation: 'horizontal'
                multiline: False
                Label:
                    text:"Min:"
                    font_size: self.width/3.5
                TextInput:
                    multiline: False
                    text: str('%.2f' % barmain.minimum)
                    font_size: self.width/3.5
                    on_text_validate:
                        root.rescale_thresh('minimum',float(self.text))
                        root.minimum = float(self.text)
                        self.text = str(root.minimum)
            BoxLayout:
                size_hint: 1 , 0.1
                orientation: 'horizontal'
                Label:
                    text:"Thresh:"
                    font_size: self.width/3.5
                TextInput:
                   #size_hint: 0.4, 1
                    multiline: False
                    text: str('%.2f' % (barmain.threshhold * (barmain.maximum-barmain.minimum) + barmain.minimum))
                    font_size: self.width/3.5
                    on_text_validate:
                        root.threshhold = (float(self.text)-barmain.minimum)/max(1,(barmain.maximum-barmain.minimum))
                        barmain.slider.value_normalized = root.threshhold
                        self.text = str('%.2f' % (barmain.threshhold * (barmain.maximum-barmain.minimum) + barmain.minimum))



[SideBar@BoxLayout]:
    content: content
    orientation: 'horizontal'
    size_hint: ctx.size_hint if hasattr(ctx, 'size_hint') else (1, 1)
    pos: 0,0
    canvas:
        Color:
            rgb: (0,0,0)
        Rectangle:
            pos: self.pos
            size: self.size
    GridLayout:
        id: content    
        spacing: 20
        padding: 10,10,10,10
        cols: 2
        # just add a id that can be accessed later on
<Root>:
    id: main
    graf: graf_ele
    bars: sb
    orientation: 'vertical'
    Button:
        center_x: root.center_x
        center_y: root.center_y
        text: 'Load Data'
        size_hint: 1, .1
        on_press:
            # what comes after `:` is basically normal python code
            graf_ele.clear_widgets()
            sb.content.clear_widgets()
            # however using a callback that you can control in python
            # gives you more control
            root.load_content(sb.content)
            root.update_metrics()
            root.load_graf(graf_ele)

            
            
    BoxLayout:
    
        Splitter:
            sizable_from: 'right'
            min_size: main.size[0]/10
            max_size: main.size[0]
            orientation: 'horizontal'
            SideBar:
                id: sb
                pos: 0,0
                size: 1,1
        RelativeLayout:
            id: graf_ele
            canvas:
                Color:
                    rgba: (0,0,1,0.1)
                Rectangle:
                    size:self.size



                

        
''')

f = "C:/Users/Spencer's/AppData/Local/Packages/Microsoft.SDKSamples.BluetoothGattHeartRate.JS_8wekyb3d8bbwe/LocalState/rrFile.txt"

#arduino = serial.Serial('COM4', 9600)

## Class for controlling Arduino motor outputs
class MotorControl():
    global arduino
    def pulse(self,duration,motor):
        print ("Duration: " + str(duration))
        print ("Motor: " + str(motor))
        self.motorOn(motor)
        Clock.schedule_once(self.motorOff ,duration) # waits for duration

 
    def motorOn(motor):
        if motor == 0:
            arduino.write('H'.encode())
        elif motor == 1:
            arduino.write('J'.encode())

    def motorOff(motor):
        #motor = round (motor)
        #print ("Motor " + str(motor) + " is now off!!")
        arduino.write('L'.encode())
        arduino.write('K'.encode())
        #if motor == 0:
            #arduino.write('L'.encode())
        #elif motor == 1:
            #arduino.write('K'.encode())
            

class FeedbackBarWidget(BoxLayout):
    global metrics
    minimum = NumericProperty(0)
    maximum = NumericProperty(1)
    slider = ObjectProperty(None)
    current = NumericProperty(0)
    threshhold = BoundedNumericProperty(0.5, min=0,max=1,errorvalue=1)
    r = NumericProperty()
    g = NumericProperty()
    b = NumericProperty()

    NumId = NumericProperty()
    def __init__(self,**kwargs):
        super(FeedbackBarWidget,self).__init__(**kwargs)
        self.current = metrics[self.NumId][1][2]
        self.threshhold = 0.5
        self.get_colour()
        if self.minimum == self.maximum:
            self.maximum += 1


    def on_current(self,barobj,current):
        global metrics
        M = self.maximum
        m = self.minimum
        if M <= self.current: #Maxiumum Rescaling
            newmax = self.current + 1
            self.rescale_thresh('maximum',newmax)
            self.maximum = newmax
        if m >= self.current: #Minimum Rescaling
            newmin = max(-10,self.current - 1)
            self.rescale_thresh('minimum',newmin)
            self.minimum = newmin
##        if len(metrics[0]) == 3:
##            self.set_min_max
        
        if self.threshhold *(M-m) + m > self.current and self.current < 30:#RMSSD ALERT
            #MotorControl.pulse(MotorControl,2,self.NumId)
            print("RMSSD EVENT")
        elif self.threshhold *(M-m) + m < self.current and self.current > 45:
            #MotorControl.pulse(MotorControl,2,self.NumId)
            print("BPM EVENT")
            
    def rescale_thresh(self,adjustment,n):
        m = self.minimum
        M = self.maximum
        if adjustment == 'minimum':
            self.threshhold = (self.threshhold*(M-m) + m-n)/(M-n)
        elif adjustment == 'maximum': #and M < n
            self.threshhold = self.threshhold * (M-m)/(n-m)
    def get_colour(self):
        self.r = metrics[self.NumId][1][0]
        self.g = metrics[self.NumId][1][1]
        self.b = metrics[self.NumId][1][2]

    def update_bounds(self):
        self.property('current').set_min(self, self.minimum)
        self.property('current').set_max(self, self.maximum)
    def updated_min(self): #Get minimum from latest 30
        val=min(metrics[self.NumId][2:31],key=itemgetter(1))[1]
        return val
    def updated_max(self): #Get maximum from latest 30
        val=max(metrics[self.NumId][2:31],key=itemgetter(1))[1]
        if val == min(metrics[self.NumId][2:30],key=itemgetter(1))[1]:
            val += 1
        return val
    def set_min_max(self):
        self.minimum = self.current * 0.8
        self.minimum = self.current * 1.2
    def zero_thresh(self):
        if self.threshhold == 0:
            self.parent.clear_widgets()
    def remove_widg(widg):
        widg.parent.remove_widget(widg)
       

class SideBar(BoxLayout):
    def zero_thresh(self,bar):
        if bar.threshhold == 0:
            self.content.remove_widget(bar)    
## Root class for Kivy App
class Root(BoxLayout):
    def check_update(self,other):
        global latest,f,metrics
        try:
            CurrentTime = os.stat(f).st_mtime
        except:
            CurrentTime = latest
        if CurrentTime == latest:
            pass

            #print ("Nothing new @ " + str(current))
        else:
            #print("Update @ " + str(CurrentTime))
            self.update_metrics()
            self.graf.clear_widgets() #Wipe current plot
            Root.load_graf(self,self.graf)

            
            latest = CurrentTime  #Update latest

    def load_content(self,content):
        global metrics        
        for metric in metrics:
            content.add_widget(FeedbackBarWidget(id = str(metric[0]),NumId = metrics.index(metric)))
    def update_metrics(self):
        global metrics,scaledmetrics
        try:
            RRData = ReadData()
        except:
            #delay(50)
            self.update_metrics()
            return
        n=30
        for DataArray in metrics:
            indi = metrics.index(DataArray) #Gets index number
            metric = DataArray[0] #Metric Name as string
            colour = DataArray[1] # Colour as RGB tuple
            M = 1
            m = 0
            try:
                pos = metrics[-1][2][0]  #Integer value of how many data points there have been
            except:
                pos = 0
            try:
                currentval= getattr(RRMetrics, metric)(RRData,n) #Convert RR values to Metric Value
                if currentval == []:
                    currenval = 0
            except:
                currentval = 0
                
            DataArray.insert(2,(pos+1,currentval)) #Insert new metric value to database
            
            for bar in self.bars.content.children:
                if metric == bar.id:
                    bar.current = float(currentval)
                    M = bar.maximum
                    m = bar.minimum
            scaledmetrics[indi] = DataArray[:2]
            for tup in DataArray[2:n+1]:
                try:
                    scaledtup = (tup[0],(tup[1] - m)*100/(M-m))
                    scaledmetrics[indi].insert(2,scaledtup)
                except:
                    pass
            
    def load_graf(self,graf): #loads graph, updates global variable metrics with newest data0
        global metrics, scaledmetrics
        graf.clear_widgets()
        try:
            RRData = ReadData()
        except:
            pass
        n=30 # n is currently used for RRMetrics and the number of points graphed. Split this
    
        try:
            pos = metrics[0][2][0]  #Integer value of how many data points there have been
        except:
            pos = 0
        graph = (Graph(xlabel = 'Data Point', ylabel = '% of Maximum', x_ticks_minor =1,
        x_ticks_major=2, y_ticks_minor=5,y_ticks_major=25,y_grid_label=True,x_grid_label=True,
        padding=5,x_grid=True,y_grid=True,xmin=max(0,pos-n+1),xmax=max(1,pos+1),ymin=0,ymax=100)) #Mod ymax/min based on bars xD


        for DataArray in scaledmetrics:
            metric = DataArray[0] #Metric Name as string
            colour = DataArray[1] #Metric colour
            plot = MeshLinePlot(color = colour)
            plot.points = tuple(DataArray[2:32]) #Replace 32 with some n variable

            plot.size = (1,1,100,100)
            graph.add_plot(plot)

        
        graf.add_widget(graph)

# List of tuples containing metric name and corresponding colour (R,G,B) 
metrics = [['BPM',(1,0,1)],['RMSSD',(0,1,0)]]
scaledmetrics = [['BPM',(1,0,1)],['RMSSD',(0,1,0)]]

#metrics = [['GetBPM',(1,0,1)],['GetRMSSD',(0,1,0)],['getFitgra',(1,1,0)],['getApEn',(0,1,1)],['pNNx',(0,0.5,1)],['sdNN',(1,0.5,0)]] #GLOBAL DATA HOLDER
#scaledmetrics = [['GetBPM',(1,0,1)],['GetRMSSD',(0,1,0)],['getFitgra',(1,1,0)],['getApEn',(0,1,1)],['pNNx',(0,0.5,1)],['sdNN',(1,0.5,0)]]
latest = []  #Holds the last point that was plotted
class TutorialApp(App):
    def build(self):
        
        application = Root()
        Clock.schedule_interval(application.check_update,0.5)  #Maybe update frequency should be > 0.5 eventually
        return application

if __name__ == "__main__":
    TutorialApp().run()

