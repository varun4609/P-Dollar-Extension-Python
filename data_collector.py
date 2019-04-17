# import matplotlib
# matplotlib.use('Agg')
from recognizer import PDollar, Template, Point
import Tkinter as tk
import trial
import xml.etree.cElementTree as ET

class ExampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.previous_x = self.previous_y = 0
        self.x = self.y = 0
        self.stroke_count = 0
        self.dict = {}
        self.points_recorded = []
        self.canvas = tk.Canvas(self, width=400, height=400, bg = "white", cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)


        # row = tk.Frame(self)
        # lab = tk.Label(row, width=15, text="Enter user ID", anchor='w')
        # self.ent = tk.Entry(row)
        # row.pack(side="top", fill=tk.X, padx=5, pady=5)
        # lab.pack(side="left")
        # self.ent.pack(side="right", expand="yes", fill=tk.X)

        # self.radbuttonval = tk.IntVar()
        # self.rad1 = tk.Radiobutton(self, text='scrollup', value=1, variable=self.radbuttonval)
        # self.rad2 = tk.Radiobutton(self,text='scrolldown', value=2, variable=self.radbuttonval)
        # self.rad3 = tk.Radiobutton(self,text='swipeleft', value=3, variable=self.radbuttonval)
        # self.rad4 = tk.Radiobutton(self,text='swiperight', value=4, variable=self.radbuttonval)
        # self.rad1.pack(side="left", padx=5)
        # self.rad2.pack(side="left", padx=5)
        # self.rad3.pack(side="left", padx=5)
        # self.rad4.pack(side="left", padx=5)

        self.button_print = tk.Button(self, text = "Save Gesture", command = self.print_points)
        self.button_print.pack(side="bottom", fill="both", expand=True)
        self.button_clear = tk.Button(self, text = "Clear", command = self.clear_all)
        self.button_clear.pack(side="bottom", fill="both", expand=True)
        self.canvas.bind("<Motion>", self.tell_)
        self.canvas.bind("<B1-Motion>", self.draw_)
        self.canvas.bind("<ButtonRelease-1>", self.save_)
        self.template_list = trial.load_for_exe()['template_list_exe']

    '''
    save

    input: event
    output: none

    Saves the current gesture drawn on the canvas into an array.
    '''
    def save_(self, event):
        self.x = event.x
        self.y = event.y
        self.canvas.create_line(self.previous_x, self.previous_y, 
                                self.x, self.y,fill="yellow")
        self.points_recorded.append(self.previous_x)
        self.points_recorded.append(self.previous_y)
        self.points_recorded.append(self.x)     
        self.points_recorded.append(self.x)        
        self.previous_x = self.x
        self.previous_y = self.y

        self.dict[self.stroke_count] = self.points_recorded
        self.points_recorded = []
        self.stroke_count += 1

    def clear_all(self):
        self.canvas.delete("all")
        self.dict = {}

    def print_points(self):
        if self.points_recorded:
            self.points_recorded.pop()
            self.points_recorded.pop()
        
        rec_list = []
        order = 0
        root = ET.Element('Gesture')

        for key, point_list in self.dict.items():
            stroke = ET.SubElement(root, 'Stroke', index='0')
            order = 0
            for item in point_list:
                if point_list.index(item) % 2 == 0:
                    if point_list.index(item) == len(point_list) - 1:
                        continue
                    point = ET.SubElement(stroke, 'Point', Order=str(order), X=str(item), Y=str(point_list[point_list.index(item) + 1]))
                    order += 1

        tree = ET.ElementTree(root)
        tree.write('test-readings.xml')

    
    '''
    tell_(self, event)

    Reads the current co-ordinates of the mouse pointer
    '''          

    def tell_(self, event):
        self.previous_x = event.x
        self.previous_y = event.y

    def draw_(self, event):
        if self.points_recorded:
            self.points_recorded.pop()
            self.points_recorded.pop()

        self.x = event.x
        self.y = event.y
        self.canvas.create_line(self.previous_x, self.previous_y, 
                                self.x, self.y,fill="yellow")
        self.points_recorded.append(self.previous_x)
        self.points_recorded.append(self.previous_y)
        self.points_recorded.append(self.x)     
        self.points_recorded.append(self.x)        
        self.previous_x = self.x
        self.previous_y = self.y

'''
Entry point for the canvas application. This calls the main function
which then starts up the algorithm and reads the data files.

'''
if __name__ == "__main__":
    app = ExampleApp()
    app.mainloop()