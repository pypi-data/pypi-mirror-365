# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
"""
Backbone modules.
"""
from torch import nn
from .position_encoding import build_position_encoding
#from backbones.PyramidalCNN import PyramidalCNN
from .position_encoding import Joiner



class Backbone(nn.Module):
    """
    BackBone class that contains the common functionality that a backbone provides
    """

    def __init__(self, input_shape, output_shape, model_class, kernel_size=32, nb_filters=16,
                 use_residual=False, depth=12):
        super().__init__()
        if model_class.__name__ == 'AttentionCNN':
            # AttentionCNN has some specific parameters
            self.attention_cnn = True
            input_channels = input_shape[1]
            input_width = input_shape[0]
            output_channels = output_shape[1]
            self.model = model_class(
                input_channels=input_channels, 
                input_width=input_width, 
                output_channels=output_channels, 
                predicted_error=False, 
                depth=depth, 
                mode='1DT',
                use_residual=use_residual,
                nb_features = 64,
                kernel_size=(32,32), 
                saveModel_suffix='', 
                multitask=False, 
                use_SEB = True, 
                use_self_attention=True,
                use_variable_length_input = False)
        else:
            self.attention_cnn = False
            self.model = model_class(input_shape=input_shape, output_shape=output_shape, kernel_size=kernel_size,
                                 nb_filters=nb_filters, use_residual=use_residual, depth=depth)
        self.num_channels = self.model.nb_features

    def forward(self, x):
        return self.model(x)


def build_backbone(backbone, hidden_dim, timesteps, in_channels, out_channels, kernel_size, nb_filters, use_residual, backbone_depth, back_channels, back_layers):
    from .InceptionTime import Inception
    model_class = Inception
    # Build position encoding and backbone
    position_embedding = build_position_encoding(hidden_dim, pos_embedding='sine')
    backbone = Backbone(
        input_shape=(timesteps, in_channels),
        output_shape=(timesteps, out_channels),
        model_class=model_class,
        kernel_size=kernel_size,
        nb_filters=nb_filters,
        use_residual=use_residual,
        depth=backbone_depth,
                        )

    # Final model is joined backbone (CNN) output with position embedding
    model = Joiner(backbone, position_embedding)
    model.num_channels = backbone.num_channels

    return model
