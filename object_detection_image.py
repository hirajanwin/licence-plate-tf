# Imports 
import cv2
import os 
import numpy as np 
import tensorflow as tf 
import sys
sys.path.append('../')
from models.research.object_detection.utils import label_map_util
from models.research.object_detection.utils import visualization_utils as vis_utils





# Define model and image name 
FILE_VIDEO = 'video/movie.mp4'
FILE_OUTPUT = 'video/output.mp4'
cap = cv2.VideoCapture(FILE_VIDEO)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

out = cv2.VideoWriter(FILE_OUTPUT, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 
10, (frame_width, frame_height))

sys.path.append('..')

MODEL_NAME = 'training/inference_graph'
#IMAGE_NAME = 'test_073.jpg' 
PATH_TO_LABELS = 'training_mobilenet/object-detection.pbtxt'
#PATH_TO_IMAGE = IMAGE_NAME 
PATH_TO_CKPT = 'training_mobilenet/frozen_inference_graph.pb'
NUM_CLASSES = 1

# Label map loading 
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load tensorflow model into memory

detection_graph = tf.Graph() 
with detection_graph.as_default():
    od_graph_def = tf.GraphDef() 
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name = '')
    
    sess = tf.Session(graph=detection_graph)
# Define tensors for object detection classifiers
# Output tensors : 
# detection boxes, scores and classes 

with detection_graph.as_default():
    with tf.Session(graph=detection_graph):
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        # Number of object detected 
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        # Load image 
# image = cv2.imread(PATH_TO_IMAGE)
# Expand image dims 
        while(cap.isOpened()):
            ret, frame = cap.read()
            image_expanded = np.expand_dims(frame , axis = 0)
            (boxes, scores, classes, num) =  sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections], 
                feed_dict={image_tensor: image_expanded} )
            # Results visualisation 
            vis_utils.visualize_boxes_and_labels_on_image_array(
                frame, 
                np.squeeze(boxes), 
                np.squeeze(classes).astype(np.int32), 
                np.squeeze(scores), 
                category_index, 
                use_normalized_coordinates=True,
                line_thickness=8, 
                min_score_thresh=0.60)

            if ret == True:
                out.write(frame)

                cv2.imshow('Licence plate detection', frame)

                if cv2.waitKey(1) &  0xFF == ord('q'):
                    break

            else:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()