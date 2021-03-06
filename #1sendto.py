# import the necessary packages
import numpy as np
import argparse
import time
import cv2
import os,gc,sys,statistics

fileName ='cup-pic-up.webm'
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()


ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
ap.add_argument("-t", "--threshold", type=float, default=0.2,
	help="threshold when applyong non-maxima suppression")
args = vars(ap.parse_args())

#------------------------------------------------------------------
# load the COCO class labels our YOLO model was trained on
labelsPath = os.path.sep.join(["/home/abc/from-penD/imp/2/yolo-coco", "coco.names"])
LABELS = open(labelsPath).read().strip().split("\n")

# initialize a list of colors to represent each possible class label
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
	dtype="uint8")

# derive the paths to the YOLO weights and model configuration
weightsPath = os.path.sep.join(["/home/abc/from-penD/imp/2/yolo-coco", "yolov3.weights"])
configPath = os.path.sep.join(["/home/abc/from-penD/imp/2/yolo-coco", "yolov3.cfg"])

# load our YOLO object detector trained on COCO dataset (80 classes)
# and determine only the *output* layer names that we need from YOLO
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]


#------------------------------------------------------------------

# initialize the video stream, pointer to output video file, and
# frame dimensions
vs = cv2.VideoCapture(fileName)#########################################################
def shelfcame():
	writer = None
	(W, H) = (None, None)
	count=0
	items=[]
	item_pos=[]
	transortarray=[]
	temparray=[]
	

	# try to determine the total number of frames in the video file

	#------------------------------------------------------------------
	# loop over frames from the video file stream
	while True:
		# read the next frame from the file
		(grabbed, frame) = vs.read()

		# if the frame was not grabbed, then we have reached the end
		# of the stream
		if not grabbed:
			print("[cam dead]")
			break

		# if the frame dimensions are empty, grab them
		if W is None or H is None:
			(H, W) = frame.shape[:2]


		#------------------------------------------------------------------
		# construct a blob from the input frame and then perform a forward
		# pass of the YOLO object detector, giving us our bounding boxes
		# and associated probabilities
		blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),swapRB=True, crop=False)
		net.setInput(blob)
		start = time.time()
		layerOutputs = net.forward(ln)
		end = time.time()

		# initialize our lists of detected bounding boxes, confidences,
		# and class IDs, respectively
		boxes = []
		confidences = []
		classIDs = []

		#------------------------------------------------------------------
		# loop over each of the layer outputs
		for output in layerOutputs:
			# loop over each of the detections
			for detection in output:
				# extract the class ID and confidence (i.e., probability)
				# of the current object detection
				scores = detection[5:]
				classID = np.argmax(scores)
				confidence = scores[classID]

				# filter out weak predictions by ensuring the detected
				# probability is greater than the minimum probability
				if confidence > args["confidence"]:
					# scale the bounding box coordinates back relative to
					# the size of the image, keeping in mind that YOLO
					# actually returns the center (x, y)-coordinates of
					# the bounding box followed by the boxes' width and
					# height
					box = detection[0:4] * np.array([W, H, W, H])
					(centerX, centerY, width, height) = box.astype("int")

					# use the center (x, y)-coordinates to derive the top
					# and and left corner of the bounding box
					x = int(centerX - (width / 2))
					y = int(centerY - (height / 2))

					# update our list of bounding box coordinates,
					# confidences, and class IDs
					boxes.append([x, y, int(width), int(height)])
					confidences.append(float(confidence))
					classIDs.append(classID)
		#------------------------------------------------------------------
		# apply non-maxima suppression to suppress weak, overlapping
		# bounding boxes
		idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
			args["threshold"])

		# ensure at least one detection exists
		if len(idxs) > 0:
			# loop over the indexes we are keeping
			for i in idxs.flatten():
				# extract the bounding box coordinates
				(x, y) = (boxes[i][0], boxes[i][1])
				(w, h) = (boxes[i][2], boxes[i][3])

				# draw a bounding box rectangle and label on the frame
				color = [int(c) for c in COLORS[classIDs[i]]]
				cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
				claName=LABELS[classIDs[i]]
				text = "{}: {:.4f}".format(claName,confidences[i])
				cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
				cv2.putText(frame, "[calibration]", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 224, 25), 2)
				temparray=x,y,w,h
				transortarray.append(temparray)
				item_pos.append(x)
				items.append(claName)
				# count=count+1
				# print(y)
				print(items)
				for i in range(len(item_pos)):
					for j in range(i + 1, (len(item_pos))):
						if(item_pos[i] == 0):
							break
						# print(item_pos)
						change_percent = ((item_pos[j])-(item_pos[i]))
						# print(item_pos[i],"--",item_pos[j],"-->>",(change_percent))
						index=0
						if(change_percent> -5 and change_percent<10 ):
							# print("change",item_pos[j])
							item_pos[j]=0
						else:
							index=index+1
						# print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",item_pos)
				for i in range(len(item_pos)):
					if(item_pos[i] != 0):
						index = item_pos.index(item_pos[i])
						# print(index)
				for j in range(len(items)):
					if(j<=index):
						print("")
					else:
						items[j]=0
				# print(items)

				# # change_percent = ((float(current)-previous)/previous)*100
				# item_pos.append(x)
				# print(item_pos)
				# # temp1=(text.split(': '))
				# # classn=temp1[0]
				# # print(classn)
				# #
				# # items.append(classn)
				# # print(items)
				# #print(centerY)
				count=count+1
				print("----------------",count)
				if (count == 10):
					print("calibration complete")
					return items,item_pos,transortarray,index
					gc.collect()
					

				cv2.imshow('image',frame)

				if cv2.waitKey(1) == 27:
					break

					vs.release()
					cv2.destroyAllWindows()

	#------------------------------------------------------------------
		'''# check if the video writer is None
		if writer is None:
			# initialize our video writer
		##	fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		##	writer = cv2.VideoWriter("output.avi", fourcc, 30,(frame.shape[1], frame.shape[0]), True)

			# some information on processing single frame
			if total > 0:
				elap = (end - start)
				print("[INFO] single frame took {:.4f} seconds".format(elap))
				print("[INFO] estimated total time to finish: {:.4f}".format(
					elap * total), "wait..")

		# write the output frame to disk
		writer.write(frame)
	'''
	# release the file pointers
	print("[INFO] cleaning up...")
	#writer.release()
	vs.release()

#------------------------------------------------------------------
def tracking():
	# items,item_pos=test()
	items,item_pos,transortarray,index=shelfcame()
	print("transport->>",transortarray)
	print(items,item_pos,"888888",index)
	exit()
	
	tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
	tracker_type = tracker_types[7]
	if True:
		# if tracker_type == 'BOOSTING':
		#     tracker = cv2.TrackerBoosting_create()
		# if tracker_type == 'MIL':
		#     tracker = cv2.TrackerMIL_create()
		# if tracker_type == 'KCF':
		#     tracker = cv2.TrackerKCF_create()
		# if tracker_type == 'TLD':
		#     tracker = cv2.TrackerTLD_create()
		# if tracker_type == 'MEDIANFLOW':
		#     tracker = cv2.TrackerMedianFlow_create()
		# if tracker_type == 'GOTURN':
		#     tracker = cv2.TrackerGOTURN_create()
		# if tracker_type == 'MOSSE':
		#     tracker = cv2.TrackerMOSSE_create()
		if tracker_type == "CSRT":
			tracker = cv2.TrackerCSRT_create()

	# Read video
	video = cv2.VideoCapture(fileName)
	time.sleep(2)
	# Exit if video not opened.
	if not video.isOpened():
		print ("Could not open video")
		sys.exit()

	# Read first frame.
	ok, frame = video.read()
	if not ok:
		print ('Cannot read video file')
		sys.exit()

	# Define an initial bounding box
   # bbox = (287, 23, 86, 320)
	#time.sleep(10)
	# Uncomment the line below to select a different bounding box
	bbox = cv2.selectROI(frame, False)

	# Initialize tracker with first frame and bounding box
	ok = tracker.init(frame, bbox)

	while True:
		# Read a new frame
		ok, frame = video.read()
		if not ok:
			break

		# Start timer
		timer = cv2.getTickCount()

		# Update tracker
		ok, bbox = tracker.update(frame)

		# Calculate Frames per second (FPS)
		fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

		# Draw bounding box
		if ok:
			# Tracking success
			p1 = (int(bbox[0]), int(bbox[1]))
			p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
			cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
		else :
			# Tracking failure
			cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

		# Display tracker type on frame
		cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);

		# Display FPS on frame
		cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);

		# Display result
		cv2.imshow("Tracking", frame)

		# Exit if ESC pressed
		k = cv2.waitKey(1) & 0xff
		if k == 27 : break
def test():
	items =['cup', 'cup', 0, 0, 0, 0, 0, 0, 0, 0]
	item_pos = [347, 54, 0, 0, 0, 0, 0, 0, 0, 0]
	return items,item_pos

#------------------------------------------------------------------
def main():
	# test()
	# shelfcame()
	tracking()
main()
#------------------------------------------------------------------
#------------------------------------------------------------------
