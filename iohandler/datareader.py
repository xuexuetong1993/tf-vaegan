import pdb
import tensorflow as tf
import re
import os

def find_files(directory, pattern='.*\.wav'):
    '''Recursively finds all files matching the pattern.'''
    files = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if re.match(pattern, filename):
                files.append(os.path.join(root, filename))
    return files


def img_reader(
		datadir,
		img_dims,
		batch_size,
		# num_examples_per_epoch,
		pattern='.*\.jpg',
		ext='jpg',
		num_threads=10,
		# capacity=1.,
		# min_fraction_of_examples_in_queue=.2
		):
	'''
	output: [batch_size, h, w, c] images, scaled to [0., 1.]
	'''
	# [TODO] Should properly design the cap and the min
	files = find_files(datadir, pattern)
	# num_examples_per_epoch = len(files)
	
	# min_after_dequeue = int(
	# 	len(files) * min_fraction_of_examples_in_queue)

	# capacity = 10 * batch_size # + min_after_dequeue

	capacity = int(.5 * len(files))
	min_after_dequeue = int(.2 * capacity)

	if ext == 'jpg' or ext == 'jpeg':
		decoder = tf.image.decode_jpeg
	elif ext == 'png':
		decoder = tf.image.decode_png
	else:
		raise ValueError('Unsupported file type: {:s}.'.format(ext) + 
			' (only *.png and *.jpg are supported')

	with tf.variable_scope('input'):
		# [TODO] should I merge tf.train.string_input_producer with `find_files`?
		h, w, c = img_dims
		filename_queue = tf.train.string_input_producer(files)
		reader = tf.WholeFileReader()
		key, value = reader.read(filename_queue)
		img = decoder(value, channels=c)
		img = tf.image.crop_to_bounding_box(img, 0, 0, h, w)
		img = tf.to_float(img)
		img = tf.div(img, 255.)
		img = tf.expand_dims(img, 0)


		# pdb.set_trace()

		imgs = tf.train.shuffle_batch(
			[img],
			batch_size=batch_size,
			num_threads=num_threads,
			capacity=capacity,
			enqueue_many=True,
			min_after_dequeue=min_after_dequeue)

		return imgs


