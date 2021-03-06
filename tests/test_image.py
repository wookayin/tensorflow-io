# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.
# ==============================================================================
"""Tests for Image Dataset."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import tensorflow
tensorflow.compat.v1.disable_eager_execution()

from tensorflow import dtypes
from tensorflow import errors
from tensorflow import image
from tensorflow.compat.v1 import resource_loader

import tensorflow_io.image as image_io

from tensorflow import test

class ImageDatasetTest(test.TestCase):

  def test_decode_webp(self):
    """Test case for decode_webp.
    """
    width = 400
    height = 301
    channel = 4
    png_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image", "sample.png")
    with open(png_file, 'rb') as f:
      png_contents = f.read()
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image", "sample.webp")
    with open(filename, 'rb') as f:
      webp_contents = f.read()

    with self.cached_session():
      png_op = image.decode_png(png_contents, channels=channel)
      png = png_op.eval()
      self.assertEqual(png.shape, (height, width, channel))

      webp_p = image_io.decode_webp(webp_contents)
      webp_v = webp_p.eval()
      self.assertEqual(webp_v.shape, (height, width, channel))

      self.assertAllEqual(webp_v, png)


  def test_webp_file_dataset(self):
    """Test case for WebPDataset.
    """
    width = 400
    height = 301
    channel = 4
    png_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image", "sample.png")
    with open(png_file, 'rb') as f:
      png_contents = f.read()
    with self.cached_session():
      image_p = image.decode_png(png_contents, channels=channel)
      image_v = image_p.eval()
      self.assertEqual(image_v.shape, (height, width, channel))

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image", "sample.webp")

    num_repeats = 2

    dataset = image_io.WebPDataset([filename]).repeat(
        num_repeats)
    iterator = dataset.make_initializable_iterator()
    init_op = iterator.initializer
    get_next = iterator.get_next()

    with self.cached_session() as sess:
      sess.run(init_op)
      for _ in range(num_repeats):  # Dataset is repeated.
        v = sess.run(get_next)
        self.assertAllEqual(image_v, v)
      with self.assertRaises(errors.OutOfRangeError):
        sess.run(get_next)

  def test_tiff_file_dataset(self):
    """Test case for TIFFDataset.
    """
    width = 560
    height = 320
    channels = 4

    images = []
    for filename in ["small-00.png", "small-01.png", "small-02.png", "small-03.png", "small-04.png"]:
      with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image", filename), 'rb') as f:
        png_contents = f.read()
      with self.cached_session():
        image_p = image.decode_png(png_contents, channels=channels)
        image_v = image_p.eval()
        self.assertEqual(image_v.shape, (height, width, channels))
        images.append(image_v)

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image", "small.tiff")
    filename = "file://" + filename

    num_repeats = 2

    dataset = image_io.TIFFDataset([filename]).repeat(num_repeats)
    iterator = dataset.make_initializable_iterator()
    init_op = iterator.initializer
    get_next = iterator.get_next()
    with self.cached_session() as sess:
      sess.run(init_op)
      for _ in range(num_repeats):
        for i in range(5):
          v = sess.run(get_next)
          self.assertAllEqual(images[i], v)
      with self.assertRaises(errors.OutOfRangeError):
        sess.run(get_next)

if __name__ == "__main__":
  test.main()
