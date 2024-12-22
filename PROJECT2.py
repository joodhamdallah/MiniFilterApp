import cv2 as cv
import numpy as np
from tkinter import *
from tkinter import filedialog, messagebox,simpledialog
from PIL import Image, ImageTk
from fractions import Fraction


def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]) #opens a file explorer to select an image 
    if file_path:      #check if the img is selected
        load_image(file_path)   #call the load_image function
        save_menu.entryconfig(0, state=NORMAL)  #enable "Save as" option, save_menu is the "save as", and the enrtyconfig is used to configure the options of the menu entry at index 0. The entry at index 0 corresponds to the "Save as" option in the "File" menu. 

def save_as():
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[   #open file explorer to save the img
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg;*.jpeg"),
        ("Bitmap files", "*.bmp")
    ])
    if file_path:  #checks if the user wrote the path
        image.save(file_path)   #save the image using PIL

def load_image(file_path):      #takes a file path as an argument
    global image, photo_label   #declare two global variables, to be accessed outside the function
    img = cv.imread(file_path)  #read the path of img using cv
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)  #convert img to RGB format,opencv reads images in BGR format by default, but PIL and Tkinter expect imgs in RGB
    image = Image.fromarray(img)  #create a PIL Image object
    photo = ImageTk.PhotoImage(image) #create a PhotoImage object for displaying in Tkinter
    photo_label.config(image=photo) #configure the label widget 
    photo_label.image = photo       #+ to display the loaded image

def apply_greyscale():
    global image, photo_label
    img = cv.cvtColor(np.array(image), cv.COLOR_RGB2GRAY) #convert to greyscale
    image = Image.fromarray(img)   #update the image variable with the grayscale result
    photo = ImageTk.PhotoImage(image)  #create a PhotoImage object for displaying the result
    photo_label.config(image=photo)   #configure the label widget to display the grayscale image
    photo_label.image = photo

def create_filter_matrix_dialog(filter_size):  #function to matrix with spaces, according to the size of filter that the user wrote
    matrix_dialog = Toplevel(root)      #create a new top-level window (dialog) for user-defined filter input
    matrix_dialog.title("User-defined Filter")  

    entries = []   #initialize an empty list to store coefficients in it
    
    for i in range(filter_size):    #save the coefficients
        row_entries = []
        for j in range(filter_size):
            entry_var = StringVar()
            entry = Entry(matrix_dialog, textvariable=entry_var, width=5)
            entry.grid(row=i, column=j, padx=5, pady=5)
            row_entries.append(entry_var)
        entries.append(row_entries)

    def apply_filter():
        global image  
        filter_matrix = [] #empty list to store the filter coefficients
        try:
            for row in entries:  #convert the user input to numeric coefficients
                row_values = [float(Fraction(entry.get())) for entry in row]
                filter_matrix.append(row_values)
        except ValueError:
            messagebox.showerror("Invalid Coefficient", "Please enter valid numeric coefficients.") #if the coefficient is invalid 
            return

        img = np.array(image)      #convert the image to a NumPy array
        kernel = np.array(filter_matrix)         #convert the filter_matrix to a NumPy array
        img = cv.filter2D(img, -1, kernel)   #apply the user-defined filter using OpenCV

        image = Image.fromarray(img)    #update the image variable with the filtered result
        photo = ImageTk.PhotoImage(image)  #create a photo img object
        photo_label.config(image=photo)
        photo_label.image = photo

        matrix_dialog.destroy()

    apply_button = Button(matrix_dialog, text="Apply Filter", command=apply_filter) #button of apply filter
    apply_button.grid(row=filter_size, columnspan=filter_size, pady=10)



image = None  #initialize image as None
photo_label = None  #initialize photo_label as None

def apply_user_defined_filter():    
    global image, photo_label

    if image is None:     #check if the image is loaded
       messagebox.showinfo("Error", "Please open an image first.")
       return
    
    
    filter_size = simpledialog.askinteger("Filter Size", "Enter the size of the filter (odd number):", parent=root) #open the window that takes the size from user
    if filter_size is None or filter_size % 2 != 0:     #check if the filter size is odd
        create_filter_matrix_dialog(filter_size)
    else:
        messagebox.showinfo("Invalid Filter Size", "Please enter an odd number for the filter size.") #display an error message if the size is even or null
  

def apply_segmentation_filter(filter_name):
    global image, photo_label

    img = np.array(image)

    if filter_name == "Point Detection":
        kernel = np.array([[-1, -1, -1],
                           [-1,  8, -1],
                           [-1, -1, -1]])
        img = cv.filter2D(img, -1, kernel)  #-1 : the depth of the output image should be the same as the input image and depth is the number of bits used to represent the intensity values of each pixel in an image

    elif filter_name in ["Horizontal Line Detection", "+45 Line Detection", "-45 Line Detection", "Vertical Line Detection"]:
        if filter_name == "Horizontal Line Detection":
            kernel = np.array([[-1, -1, -1],
                               [ 2,  2,  2],
                               [-1, -1, -1]])
        elif filter_name == "+45 Line Detection":
            kernel = np.array([[-1, -1,  2],
                               [-1,  2, -1],
                               [ 2, -1, -1]])
        elif filter_name == "-45 Line Detection":
            kernel = np.array([[ 2, -1, -1],
                               [-1,  2, -1],
                               [-1, -1,  2]])
        elif filter_name == "Vertical Line Detection":
            kernel = np.array([[-1,  2, -1],
                               [-1,  2, -1],
                               [-1,  2, -1]])
        img = cv.filter2D(img, -1, kernel)

    elif filter_name in ["Horizontal Edge Detection (Sobel)", "Vertical Edge Detection (Sobel)", "+45 Edge Detection (Sobel)", "-45 Edge Detection (Sobel)"]:
        if filter_name == "Horizontal Edge Detection (Sobel)":
            img = cv.Sobel(img, cv.CV_64F, 0, 1, ksize=3)
        elif filter_name == "Vertical Edge Detection (Sobel)":
            img = cv.Sobel(img, cv.CV_64F, 1, 0, ksize=3)
        elif filter_name == "+45 Edge Detection (Sobel)":
            kernel = np.array([[-2, -1,  0],
                               [-1,  0,  1],
                               [ 0,  1,  2]])
            img = cv.filter2D(img, -1, kernel)
        elif filter_name == "-45 Edge Detection (Sobel)":
            kernel = np.array([[ 0,  1, 2],
                               [-1,  0, 1],
                               [-2, -1, 0]])
            img = cv.filter2D(img, -1, kernel)

    elif filter_name in ["Horizontal Edge Detection (Prewitt)", "Vertical Edge Detection (Prewitt)", "+45 Edge Detection (Prewitt)", "-45 Edge Detection (Prewitt)"]:
        if filter_name == "Horizontal Edge Detection (Prewitt)":
            kernel = np.array([[-1, -1, -1],
                               [ 0,  0,  0],
                               [ 1,  1,  1]])
        elif filter_name == "Vertical Edge Detection (Prewitt)":
            kernel = np.array([[-1,  0,  1],
                               [-1,  0,  1],
                               [-1,  0,  1]])
        elif filter_name == "-45 Edge Detection (Prewitt)":
            kernel = np.array([[ 0,  1,  1],
                               [-1,  0,  1],
                               [-1, -1,  0]])
        elif filter_name == "+45 Edge Detection (Prewitt)":
            kernel = np.array([[-1, -1,  0],
                               [-1,  0,  1],
                               [ 0,  1,  1]])
        img = cv.filter2D(img, -1, kernel)

    elif filter_name in ["+45 Edge Detection (Roberts)", "-45 Edge Detection (Roberts)"]:
        if filter_name == "+45 Edge Detection (Roberts)":
            kernel = np.array([[-1, 0],
                               [ 0, 1]])
        elif filter_name == "-45 Edge Detection (Roberts)":
            kernel = np.array([[ 0, -1],
                               [ 1, 0]])
        img = cv.filter2D(img, -1, kernel)

    elif filter_name in ["Laplacian Filter", "Laplacian of Gaussian"]:
        if filter_name == "Laplacian Filter":
            img = cv.Laplacian(img, cv.CV_64F)
        elif filter_name == "Laplacian of Gaussian":
            img = cv.GaussianBlur(img, (5, 5), 0)
            img = cv.Laplacian(img, cv.CV_64F)

    elif filter_name in ["Thresholding", "Adaptive Thresholding"]:
        if filter_name == "Thresholding":
             threshold_value = simpledialog.askinteger("Thresholding", "Enter the threshold value:", parent=root)
             if threshold_value is not None:
              _, img = cv.threshold(img, threshold_value, 255, cv.THRESH_BINARY)


        elif filter_name == "Adaptive Thresholding":
            img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
            img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)

    elif filter_name == "Zero Crossing":
        img = cv.Canny(img, 100, 200)

    elif filter_name == "User-defined Filter":
        apply_user_defined_filter()

    image = Image.fromarray(img)
    photo = ImageTk.PhotoImage(image)
    photo_label.config(image=photo)
    photo_label.image = photo

root = Tk()
root.title('Image segmentation filters')
#root.iconbitmap('E:/imageproc_proj2/cam.ico')
root.geometry("1000x650")     #default size of the window

menu_bar = Menu(root)

file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
save_menu = Menu(file_menu, tearoff=0)
save_menu.add_command(label="Save as", command=save_as, state=DISABLED)
file_menu.add_cascade(label="Save", menu=save_menu)
menu_bar.add_cascade(label="File", menu=file_menu)

image_menu = Menu(menu_bar, tearoff=0)
mode_menu = Menu(image_menu, tearoff=0)
mode_menu.add_command(label="Greyscale", command=apply_greyscale)
image_menu.add_cascade(label="Mode", menu=mode_menu)
menu_bar.add_cascade(label="Image", menu=image_menu)

filters_menu = Menu(menu_bar, tearoff=0)
segmentation_menu = Menu(filters_menu, tearoff=0)

# Organizing segmentation filters into categories
point_detection_filters = ["Point Detection"]
line_detection_filters = ["Horizontal Line Detection", "+45 Line Detection", "-45 Line Detection", "Vertical Line Detection"]
sobel_filters = ["Horizontal Edge Detection (Sobel)", "Vertical Edge Detection (Sobel)", "+45 Edge Detection (Sobel)", "-45 Edge Detection (Sobel)"]
prewitt_filters = ["Horizontal Edge Detection (Prewitt)", "Vertical Edge Detection (Prewitt)", "+45 Edge Detection (Prewitt)", "-45 Edge Detection (Prewitt)"]
roberts_filters = ["+45 Edge Detection (Roberts)", "-45 Edge Detection (Roberts)"]
laplacian_filters = ["Laplacian Filter", "Laplacian of Gaussian"]
thresholding_filters = ["Thresholding", "Adaptive Thresholding"]
zero_crossing_filter = ["Zero Crossing"]
user_defined_filter = ["User-defined Filter"]

for filter_name in point_detection_filters:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

segmentation_menu.add_separator()

for filter_name in line_detection_filters:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

segmentation_menu.add_separator()

for filter_name in sobel_filters:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

segmentation_menu.add_separator()

for filter_name in prewitt_filters:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

segmentation_menu.add_separator()

for filter_name in roberts_filters:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

segmentation_menu.add_separator()

for filter_name in laplacian_filters:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

segmentation_menu.add_separator()

for filter_name in thresholding_filters:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

segmentation_menu.add_separator()

for filter_name in zero_crossing_filter:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

segmentation_menu.add_separator()

for filter_name in user_defined_filter:
    segmentation_menu.add_command(label=filter_name, command=lambda fn=filter_name: apply_segmentation_filter(fn))

filters_menu.add_cascade(label="Segmentation", menu=segmentation_menu)
menu_bar.add_cascade(label="Filters", menu=filters_menu)

root.config(menu=menu_bar)

photo_label = Label(root)
photo_label.grid(row=0, column=1, padx=10, pady=10)


root.mainloop()
