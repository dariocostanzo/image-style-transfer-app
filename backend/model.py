import tensorflow as tf
import numpy as np
import time
import PIL.Image

def tensor_to_image(tensor):
    tensor = tensor * 255
    tensor = np.array(tensor, dtype=np.uint8)
    if np.ndim(tensor) > 3:
        assert tensor.shape[0] == 1
        tensor = tensor[0]
    return PIL.Image.fromarray(tensor)

def load_img(path_to_img):
    max_dim = 256  # Reduced from 512
    img = tf.io.read_file(path_to_img)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)

    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim

    new_shape = tf.cast(shape * scale, tf.int32)

    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    return img

def vgg_layers(layer_names):
    vgg = tf.keras.applications.VGG19(include_top=False, weights='imagenet')
    vgg.trainable = False
    
    outputs = [vgg.get_layer(name).output for name in layer_names]
    model = tf.keras.Model([vgg.input], outputs)
    return model

def gram_matrix(input_tensor):
    result = tf.linalg.einsum('bijc,bijd->bcd', input_tensor, input_tensor)
    input_shape = tf.shape(input_tensor)
    num_locations = tf.cast(input_shape[1] * input_shape[2], tf.float32)
    return result / num_locations

class StyleContentModel(tf.keras.models.Model):
    def __init__(self, style_layers, content_layers):
        super(StyleContentModel, self).__init__()
        self.vgg = vgg_layers(style_layers + content_layers)
        self.style_layers = style_layers
        self.content_layers = content_layers
        self.num_style_layers = len(style_layers)
        self.vgg.trainable = False

    def call(self, inputs):
        inputs = inputs * 255.0
        preprocessed_input = tf.keras.applications.vgg19.preprocess_input(inputs)
        outputs = self.vgg(preprocessed_input)
        style_outputs, content_outputs = (outputs[:self.num_style_layers],
                                          outputs[self.num_style_layers:])

        style_outputs = [gram_matrix(style_output)
                         for style_output in style_outputs]

        content_dict = {content_name: value
                        for content_name, value
                        in zip(self.content_layers, content_outputs)}

        style_dict = {style_name: value
                      for style_name, value
                      in zip(self.style_layers, style_outputs)}

        return {'content': content_dict, 'style': style_dict}

# In the style_transfer function, add better error handling for saving the result

def style_transfer(content_path, style_path, output_path, update_progress=None):
    # Reduce image dimensions to save memory
    max_dim = 256  # Reduced from 512
    
    content_image = load_img(content_path)
    style_image = load_img(style_path)
    
    content_layers = ['block5_conv2'] 
    style_layers = ['block1_conv1',
                    'block2_conv1',
                    'block3_conv1', 
                    'block4_conv1', 
                    'block5_conv1']
    
    extractor = StyleContentModel(style_layers, content_layers)
    
    style_targets = extractor(style_image)['style']
    content_targets = extractor(content_image)['content']
    
    image = tf.Variable(content_image)
    
    opt = tf.optimizers.Adam(learning_rate=0.02, beta_1=0.99, epsilon=1e-1)
    
    style_weight = 1e-2
    content_weight = 1e4
    
    def style_content_loss(outputs):
        style_outputs = outputs['style']
        content_outputs = outputs['content']
        
        style_loss = tf.add_n([tf.reduce_mean((style_outputs[name] - style_targets[name])**2) 
                              for name in style_outputs.keys()])
        style_loss *= style_weight / len(style_layers)

        content_loss = tf.add_n([tf.reduce_mean((content_outputs[name] - content_targets[name])**2) 
                                for name in content_outputs.keys()])
        content_loss *= content_weight / len(content_layers)
        
        total_loss = style_loss + content_loss
        return total_loss
    
    @tf.function()
    def train_step(image):
        with tf.GradientTape() as tape:
            outputs = extractor(image)
            loss = style_content_loss(outputs)
            
        grad = tape.gradient(loss, image)
        opt.apply_gradients([(grad, image)])
        image.assign(tf.clip_by_value(image, 0.0, 1.0))
        
        return loss
    
    # Reduce the number of iterations to save memory and time
    epochs = 5  # Reduced from 10
    steps_per_epoch = 50  # Reduced from 100
    
    # Calculate total steps for progress reporting
    total_steps = epochs * steps_per_epoch
    
    # Add memory cleanup between epochs and show progress
    print("Starting style transfer (0% complete)...")
    step_count = 0
    
    # Update the progress at the start
    if update_progress:
        try:
            update_progress(0)
            print("Initial progress set to 0%")
        except Exception as e:
            print(f"Error updating initial progress: {str(e)}")
    
    # Track last reported progress to avoid duplicate updates
    last_reported_progress = 0
    
    for n in range(epochs):
        for m in range(steps_per_epoch):
            train_step(image)
            step_count += 1
            
            # Calculate current progress
            current_progress = int((step_count / total_steps) * 100)
            
            # Update progress more frequently
            if step_count % 5 == 0 or current_progress > last_reported_progress:
                print(f"Style transfer progress: {current_progress}% complete")
                
                # Update the progress
                if update_progress:
                    try:
                        update_progress(current_progress)
                        print(f"Progress updated to {current_progress}%")
                        
                        # Save intermediate result every 10% progress
                        if current_progress % 10 == 0 or current_progress >= 50:
                            try:
                                intermediate_result = tensor_to_image(image)
                                intermediate_result.save(output_path)
                                print(f"Saved intermediate result at {current_progress}% to {output_path}")
                            except Exception as e:
                                print(f"Error saving intermediate result: {str(e)}")
                    except Exception as e:
                        print(f"Error updating progress: {str(e)}")
                
                last_reported_progress = current_progress
        
        # Force garbage collection after each epoch
        import gc
        gc.collect()
    
    print("Style transfer complete (100%)!")
    # Ensure final progress is 100%
    if update_progress:
        try:
            update_progress(100)
            print("Final progress set to 100%")
        except Exception as e:
            print(f"Error updating final progress: {str(e)}")
    
    # At the end of the function, add better error handling for saving the result
    try:
        # Save intermediate results periodically
        if step_count % 25 == 0 or current_progress >= 50:
            intermediate_result = tensor_to_image(image)
            intermediate_result.save(output_path)
            print(f"Saved intermediate result at {current_progress}% to {output_path}")
    except Exception as e:
        print(f"Error saving intermediate result: {str(e)}")
    
    # At the very end of the function, ensure the final result is saved
    try:
        print("Saving final result image...")
        result = tensor_to_image(image)
        result.save(output_path)
        print(f"Final result image saved to {output_path}")
        
        # Ensure final progress is 100%
        if update_progress:
            update_progress(100)
            print("Final progress set to 100%")
    except Exception as e:
        print(f"Error saving final result image: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    # Final cleanup
    import gc
    gc.collect()
    
    return output_path