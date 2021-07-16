import tensorflow as tf

saved_model_dir = 'laneDirectionModel'
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)  # path to the SavedModel directory
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Optimize by converting all tensors to integers
# converter.inference_input_type = tf.uint8  # Change data type for input and output
# converter.inference_output_type = tf.uint8
tflite_model = converter.convert()

with open(saved_model_dir + '_Lite.tflite', 'wb') as f:
  f.write(tflite_model)