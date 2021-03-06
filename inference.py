import tensorflow as tf
import cv2
import numpy as np
from parameters import *


def get_weight(shape):
    return tf.get_variable("weight", shape, initializer=tf.truncated_normal_initializer(stddev=0.1))


def get_bias(shape):
    return tf.get_variable("bias", shape, initializer=tf.constant_initializer(0.0))


def inference(input_tensor, train, regularizer):
    # 第一层，输出32*32*conv1_depth
    with tf.variable_scope("conv1"):
        conv1_weights = get_weight([CONV1_SIZE, CONV1_SIZE, NUM_CHANNELS, CONV1_DEPTH])
        conv1_biases = get_bias([CONV1_DEPTH])
        conv1 = tf.nn.conv2d(input_tensor, conv1_weights, strides=[1, 1, 1, 1],padding='SAME')
        # same padding in tensorflow意味着使输出维度为int(img_size/stride)
        relu1 = tf.nn.relu(tf.nn.bias_add(conv1, conv1_biases))
    with tf.name_scope("pooling1"):
        pooling1 = tf.nn.max_pool(relu1, ksize=[1, 2, 2, 1], 
                        strides=[1, 2, 2, 1], padding='SAME')
    # 第二层输出16*16*conv2_depth
    with tf.variable_scope("conv2"):
        conv2_weights = get_weight([CONV2_SIZE, CONV2_SIZE, CONV1_DEPTH, CONV2_DEPTH])
        conv2_biases = get_bias([CONV2_DEPTH])
        conv2 = tf.nn.conv2d(pooling1, conv2_weights, strides=[1,1,1,1], padding="SAME")
        relu2 = tf.nn.relu(tf.nn.bias_add(conv2, conv2_biases))
    with tf.name_scope("pooling2"):
        pooling2 = tf.nn.max_pool(relu2, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')
    # 第三层，输出8*8*conv3_depth
    with tf.variable_scope("conv3"):
        conv3_weights = get_weight([CONV3_SIZE, CONV3_SIZE, CONV2_DEPTH, CONV3_DEPTH])
        conv3_biases =get_bias([CONV3_DEPTH])
        conv3 = tf.nn.conv2d(pooling2, conv3_weights, strides=[1,1,1,1], padding='SAME')
        relu3 = tf.nn.relu(tf.nn.bias_add(conv3, conv3_biases))
    with tf.name_scope("pooling3"):
        pooling3 = tf.nn.max_pool(relu3, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')


    conv_out_shape = pooling3.get_shape()
    nodes = conv_out_shape[1]*conv_out_shape[2]*conv_out_shape[3]
    # 根据第二个维度调整第一维度
    fc_input = tf.reshape(pooling3, [-1, nodes])
    # 第一层全连接
    with tf.variable_scope('fc_layer_1'):
        fc_weights_1 = get_weight([nodes, FC1_SIZE])
        if regularizer !=None:
            tf.add_to_collection("losses", regularizer(fc_weights_1))
        fc_biases_1 = get_bias([FC1_SIZE])
        fc_layer_1 = tf.nn.relu(tf.matmul(fc_input, fc_weights_1)+fc_biases_1)
        # 只在全连接层且是训练时才需要dropout
        if train: fc_layer_1 = tf.nn.dropout(fc_layer_1, 0.5)
    # 第二层全连接
    with tf.variable_scope("fc_layer_2"):
        fc_weights_2 = get_weight([FC1_SIZE, OUTPUT_SIZE])
        if regularizer !=None:
            tf.add_to_collection("losses", regularizer(fc_weights_2))
        fc_biases_2 = get_bias([OUTPUT_SIZE])
        logit = tf.matmul(fc_layer_1, fc_weights_2) + fc_biases_2
    return logit
    
    