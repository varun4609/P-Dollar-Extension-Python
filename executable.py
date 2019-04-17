from recognizer import PDollar, Template, Point
from PIL import ImageTk, Image
import Tkinter as tk
import trial

class ExampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.previous_x = self.previous_y = 0
        self.x = self.y = 0
        self.stroke_count = 0
        self.dict = {}
        self.points_recorded = []

        self.leftFrame = tk.Frame(self)
        self.leftFrame.pack(side=tk.LEFT)
        self.rightFrame = tk.Frame(self)
        self.rightFrame.pack(side=tk.RIGHT)

        import_img = ImageTk.PhotoImage(Image.open("Gesture_Image_1.png"))
        self.img = tk.Label(self.rightFrame, image = import_img)
        self.img.image = import_img
        self.img.pack()

        self.topFrame = tk.Frame(self.leftFrame)
        self.topFrame.pack()
        self.bottomFrame = tk.Frame(self.leftFrame)
        self.bottomFrame.pack(side=tk.BOTTOM)

        self.bottomSubFrame1 = tk.Frame(self.bottomFrame)
        self.bottomSubFrame1.pack()

        self.bottomSubFrame2 = tk.Frame(self.bottomFrame)
        self.bottomSubFrame2.pack(side=tk.BOTTOM, fill=tk.Y, pady = 5)

        self.canvas = tk.Canvas(self.topFrame, width=400, height=400, bg = "white", cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.result_label = tk.Label(self.bottomSubFrame1, text = "Result: ")
        self.result_label.pack()

        self.result_box = tk.Text(self.bottomSubFrame1, height=1, width = 55)
        self.result_box.pack(side="bottom", fill="both", expand=True)

        self.button_print = tk.Button(self.bottomSubFrame2, text = "Recognize", width = 30, bg= "gray", command = self.print_points)
        self.button_print.pack(side=tk.LEFT, fill="both", expand=True, padx=10)
        
        self.button_clear = tk.Button(self.bottomSubFrame2, text = "Clear", width = 30, bg= "gray", command = self.clear_all)
        self.button_clear.pack(side=tk.LEFT, fill="both", expand=True, padx=10)
        
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
                                self.x, self.y,fill="black")
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
        self.result_box.delete(1.0, tk.END)
        self.dict = {}
        self.stroke_count = 0

    def print_points(self):
        if self.points_recorded:
            self.points_recorded.pop()
            self.points_recorded.pop()
        
        rec_list = []
        for key, point_list in self.dict.items():
            for item in point_list:
                if point_list.index(item) % 2 == 0:
                    if point_list.index(item) == len(point_list) - 1:
                        continue
                    rec_list.append(Point(item, point_list[point_list.index(item) + 1], key))

        print(list(self.dict.keys()))

        recognizer = PDollar(self.template_list)

        x_diff = rec_list[0].x - rec_list[-1].x
        y_diff = rec_list[0].y - rec_list[-1].y
        res_str = ''
        if abs(x_diff) > abs(y_diff):
            res_str += 'swipe'
            if rec_list[0].x > rec_list[-1].x:
                res_str += '_left'
            else:
                res_str += '_right'
        else:
            res_str += 'scroll'
            if rec_list[0].y > rec_list[-1].y:
                res_str += '_up'
            else:
                res_str += '_down'

        result = recognizer.recognize(rec_list)
        print(result[0])
        print(result[1])
        self.result_box.insert(tk.INSERT, res_str)

    
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
                                self.x, self.y,fill="black")
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