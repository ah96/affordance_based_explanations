import csv
from PIL import Image


def convert_csv_to_png(csv_file, png_file):
    # Read pixel values from CSV
    with open(csv_file, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        data_loaded = list(reader)[0:]

    print('data_loaded:')
    print((len(data_loaded), len(data_loaded[0])))

    data_all = []
    for i in range(0, 700):
        data_all.append([205] * (1984))        

    for i in range(0, len(data_loaded)):
        row = [205] * (700) + data_loaded[i] + [205] * (1984-1200)
        data_all.append(row)    

    for i in range(0, 1984 - len(data_all)):
        data_all.append([205] * (1984))

    height = len(data_all)
    width = len(data_all[0])

    print('data_all:')
    print((len(data_all),len(data_all[0])))

    # Create a new image from pixel values
    image = Image.new('L', (width, height))
    pixels = [int(pixel) for row in data_all for pixel in row]
    #print(pixels[-100:-1])
    image.putdata(pixels)

    # Save the image as PNG
    image.save(png_file)


# Usage example
csv_file = 'map.csv'
png_file = 'map_final.png'

convert_csv_to_png(csv_file, png_file)
