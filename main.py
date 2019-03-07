import numpy
import random
import math
from PIL import Image

# image width and height are statically defined
dimension = 4000

def getPixelFromBytes(bytes, c_divisions):
	value = 0
	for i in range(len(bytes)):
		value += 256**i * bytes[i]
	
	return getPixelFromValue(value, c_divisions)

def getBytesFromPixel(pixel, c_divisions, bytesPerPDivision):
	value = getValueFromPixel(pixel, c_divisions)
	
	bytes = []
	for i in range(bytesPerPDivision):
		bytes.append(value % 256)
		value //= 256
	
	if value > 0:
		print("Unexpected remainder in getBytesFromPixel")
	
	return bytes
	

def getPixelFromValue(value, c_divisions):
	def getColorFromValue(value):
		return value % c_divisions / (c_divisions - 1) * 255
	
	pix = [];
	pix.append(getColorFromValue(value))
	value //= c_divisions
	pix.append(getColorFromValue(value))
	value //= c_divisions
	pix.append(getColorFromValue(value))
	value //= c_divisions
	
	if value > 0:
		print("Unexpected remainder in getPixelFromValue")
	
	return pix

def getCDivisionFromColor(color, c_divisions):
	c_div = round(color * (c_divisions - 1) / 255)
	if c_div < 0:
		c_div = 0
	if c_div >= c_divisions:
		c_div = c_divisions - 1
	return c_div

def getValueFromPixel(pixel, c_divisions):
	value = getCDivisionFromColor(pixel[0], c_divisions)
	value += getCDivisionFromColor(pixel[1], c_divisions) * c_divisions
	value += getCDivisionFromColor(pixel[2], c_divisions) * c_divisions * c_divisions
	return value

def writeBytesToFile(bytes, bytesPerPDivision, p_divisions, c_divisions, file):
	pixels = numpy.zeros((dimension, dimension, 3))
	
	byte_index = 0
	
	for div_row in range(p_divisions):
		for div_col in range(p_divisions):
			# create a pixel from the bytes with the appropriate color divisions
			pixel_bytes = bytes[byte_index:(byte_index + bytesPerPDivision)]
			pix = getPixelFromBytes(pixel_bytes, c_divisions)
			byte_index += bytesPerPDivision
			
			# find the pixel row beginning and end
			pix_row_beg = round((div_row) / p_divisions * dimension)
			pix_row_end = round((div_row + 1) / p_divisions * dimension)
			
			# find the pixel column beginning and end
			pix_col_beg = round((div_col) / p_divisions * dimension)
			pix_col_end = round((div_col + 1) / p_divisions * dimension)
			
			# populate the pixels in this division
			for pix_row in range(pix_row_beg, pix_row_end):
				for pix_col in range(pix_col_beg, pix_col_end):
					pixels[pix_row][pix_col] = pix
	
	print('writing to file')
	im_out = Image.fromarray(numpy.array(pixels).astype('uint8')).convert('RGB')
	im_out.save(file)

def readBytesFromFile(bytesPerPDivision, p_divisions, c_divisions, file):
	print('reading from:', file)
	im_in = Image.open(file)
	print('done')
	
	pixels = im_in.getdata()
	
	# average the colors for each division
	avg_pixels = numpy.zeros((p_divisions, p_divisions, 4))
	
	read_bytes = [];
	
	div_margin = 0.2
	
	for i in range(len(pixels)):
		div_row = (int(i / dimension) + 0.5) * (p_divisions / dimension)
		div_col = (i % dimension + 0.5) * (p_divisions / dimension)
		
		if  div_row - int(div_row) >= div_margin and \
			div_row - int(div_row) <= 1 - div_margin and \
			div_col - int(div_col) >= div_margin and \
			div_col - int(div_col) <= 1 - div_margin:
			avg_pixels[int(div_row)][int(div_col)][0] += pixels[i][0]
			avg_pixels[int(div_row)][int(div_col)][1] += pixels[i][1]
			avg_pixels[int(div_row)][int(div_col)][2] += pixels[i][2]
			avg_pixels[int(div_row)][int(div_col)][3] += 1
	
	for div_row in range(p_divisions):
		for div_col in range(p_divisions):
			# compute the averages for each pixel division
			avg_pixels[div_row][div_col][0] /= avg_pixels[div_row][div_col][3]
			avg_pixels[div_row][div_col][1] /= avg_pixels[div_row][div_col][3]
			avg_pixels[div_row][div_col][2] /= avg_pixels[div_row][div_col][3]
			
			read_bytes += getBytesFromPixel(avg_pixels[div_row][div_col], c_divisions, bytesPerPDivision)
	
	return read_bytes
	
def getBytesForPDivisionsAndCDivisions(p_divisions, c_divisions):
	# calculate how many bytes can be stored in a pixel division
	combinations = c_divisions * c_divisions * c_divisions
	bytesPerPDivision = int(math.log2(combinations) / 8)
	bytes = p_divisions * p_divisions * bytesPerPDivision
	
	# test the validity of this configuration for a random string of bytes
	random_bytes = []
	for i in range(bytes):
		random_bytes.append(random.randint(0,255))
	
	writeBytesToFile(random_bytes, bytesPerPDivision, p_divisions, c_divisions, 'test.jpg')
	#print(random_bytes)
	check_bytes = readBytesFromFile(bytesPerPDivision, p_divisions, c_divisions, 'test.jpg')
	#print(check_bytes)
	
	valid = True
	for i in range(len(random_bytes)):
		if random_bytes[i] != check_bytes[i]:
			valid = False
			break
	
	if valid:
		return bytes
	else:
		return 0

# perform a binary search for the pixel divisions that will validly produce maximum bytes
def getMaxBytesForCDivisions(c_divisions, min_p_divisions, max_p_divisions):
	mid_p_divisions = (min_p_divisions + max_p_divisions) // 2
	
	mid_bytes = getBytesForPDivisionsAndCDivisions(mid_p_divisions, c_divisions)
	print(mid_p_divisions, ':', mid_bytes)
	
	if min_p_divisions <= mid_p_divisions - 1 and mid_bytes == 0:
		return getMaxBytesForCDivisions(c_divisions, min_p_divisions, mid_p_divisions - 1)
	if mid_p_divisions + 1 <= max_p_divisions and mid_bytes > 0:
		(p_divisions, max_bytes) = getMaxBytesForCDivisions(c_divisions, mid_p_divisions + 1, max_p_divisions)
		if max_bytes > mid_bytes:
			return (p_divisions, max_bytes)
	
	return (mid_p_divisions, mid_bytes)

print('getting max bytes for divisions')

p_divisions = None
c_divisions = None
bytes_max = None
for temp_c_divisions in (7, 41, 256):
	(temp_p_divisions, temp_bytes_max) = getMaxBytesForCDivisions(temp_c_divisions, 1, dimension)
	if temp_bytes_max > 0:
		if bytes_max == None or temp_bytes_max > bytes_max:
			p_divisions = temp_p_divisions
			c_divisions = temp_c_divisions
			bytes_max = temp_bytes_max
print('pixel divisions:', p_divisions, ',', 'color divisions:', c_divisions, ',', 'max bytes:', bytes_max)

#getMaxBitsForDivisions(2, 10)
