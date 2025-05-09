import gradio as gr
import numpy as np
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
# Load your trained model
model = tf.keras.models.load_model("rwcnet.h5")

# Your categories
categories = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model([img_array, img_array])
        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    # Gradient of the class wrt output feature map
    grads = tape.gradient(class_channel, conv_outputs)

    # Mean intensity of gradient for each feature map channel
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Multiply each channel in feature map array by the importance
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Normalize between 0 and 1
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()
# Predict function for Gradio
def predict_and_explain(image):
    # Resize and normalize image
    img = cv2.resize(image, (224, 224))
    img_normalized = img / 255.0
    input_tensor = np.expand_dims(img_normalized, axis=0)

    # Predict
    preds = model.predict([input_tensor, input_tensor])
    pred_label = np.argmax(preds[0])
    pred_confidence = preds[0][pred_label]
    label_str = f"{categories[pred_label]} ({pred_confidence*100:.2f}%)"

    # Grad-CAM
    heatmap = make_gradcam_heatmap(input_tensor, model, last_conv_layer_name="Conv_1")
    img_for_cam = show_gradcam(img_normalized, heatmap, alpha=0.4)

    return label_str, img_for_cam
def show_gradcam(img, heatmap, alpha=0.4):
    img = np.uint8(255 * img)  # Scale back to [0, 255]
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap = np.uint8(255 * heatmap)
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    superimposed_img = cv2.addWeighted(img, 1 - alpha, heatmap_color, alpha, 0)
    superimposed_img = cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB)
    return superimposed_img  # Return image instead of plotting

interface = gr.Interface(
    fn=predict_and_explain,
    inputs=gr.Image(type="numpy", label="Upload Image"),
    outputs=[gr.Label(label="Prediction"), gr.Image(label="Grad-CAM")],
    title="Waste Classification with RWCNet",
    description="Upload a waste image to classify it and visualize model attention using Grad-CAM."
)

interface.launch()
grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
resized = cv2.resize(grayscale, (224, 224))
processed_img = np.stack((resized,)*3, axis=-1) / 255.0
input_tensor = np.expand_dims(processed_img, axis=0)
