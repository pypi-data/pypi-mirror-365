
"""
DeTR implementation, rewritten for time series segmentation adjusted for Scanpath prediction
"""
import torch
import torch.nn.functional as F
import torch.nn as nn
from .transformer import build_transformer
from .backbone import build_backbone
from huggingface_hub import hf_hub_download

class UnifiedScanpathDecoder(nn.Module):
    """ This is the DETR module that performs object detection """
    def __init__(self, num_classes, num_queries, backbone, hidden_dim, timesteps, in_channels, out_channels, kernel_size, nb_filters, use_residual, backbone_depth, back_channels, back_layers, nheads, enc_layers, dec_layers, dim_feedforward, dropout, pre_norm):
        """ Initializes the model for screen polar coordinates.
        Parameters:
            backbone: torch module of the backbone to be used. See backbone.py
            transformer: torch module of the transformer architecture. See transformer.py
            num_classes: number of object classes
            num_queries: number of object queries, ie detection slot. This is the maximal number of objects
                         DETR can detect in a single image. For COCO, we recommend 100 queries.
            head: "fixation_only" or "all" to include saccade and blink predictions
            predicted_error: True if auxiliary decoding losses (loss at each decoder layer) are to be used.
        """
        super().__init__()
        # Model parameters

        self.num_classes = num_classes
        self.num_queries = num_queries

        # Build Backbone
        self.backbone = build_backbone(backbone, hidden_dim, timesteps, in_channels, out_channels, kernel_size, nb_filters, use_residual, backbone_depth, back_channels, back_layers)
        # Build Transformer
        self.transformer = build_transformer(hidden_dim, nheads, enc_layers, dec_layers, dim_feedforward, dropout, pre_norm)
        self.hidden_dim = self.transformer.d_model
        # Backbone-to-Transformer projection
        self.input_proj = nn.Conv1d(self.backbone.num_channels, self.hidden_dim, 1) # ! Dimension after transformer = "hidden_dim"
        # Defining heads based on perspective, coordinate system, loss type, and head type
        self._init_heads()

    def _init_heads(self):
        """
        Initialize heads for screen polar configuration
        """

        # Eye type
        self.class_embed = nn.Linear(self.hidden_dim, self.num_classes + 1)
        
        # Outputs two values for bounding box
        self.bbox_embed = MLP(self.hidden_dim, self.hidden_dim, 2, 3)
        self.query_embed = nn.Embedding(self.num_queries, self.hidden_dim)

        # Screen polar fixation heads
        self.fix_screen_angle = MLP(self.hidden_dim, self.hidden_dim, 1, 3)
        self.fix_euclidean_distance = MLP(self.hidden_dim, self.hidden_dim, 1, 3)
        
        self.sac_relative_screen_angle = MLP(self.hidden_dim, self.hidden_dim, 1, 3)
        self.sac_relative_euclidean_distance = MLP(self.hidden_dim, self.hidden_dim, 1, 3)
        self.blink_relative_screen_angle = MLP(self.hidden_dim, self.hidden_dim, 1, 3)
        self.blink_relative_euclidean_distance = MLP(self.hidden_dim, self.hidden_dim, 1, 3)
    

    def forward(self, samples: torch.Tensor): 
        """ The forward expects a NestedTensor, which consists of:
        In:
               - samples.tensor: batched images, of shape [batch_size x C x S]
           
        Out:
               - dict with predictions (defined below) and possibly predicted errors
        """
        backbone_out, positional_encoding = self.backbone(samples)
        hs = self.transformer(self.input_proj(backbone_out), None, self.query_embed.weight, positional_encoding)[0]
        
        # Build the output dictionary
        eye_type_out = self.class_embed(hs)
        pred_boxes = self.bbox_embed(hs).sigmoid()

        out = {'predictions': {
            'eye_type': eye_type_out[-1],
            'pred_boxes': pred_boxes[-1],
            'fix_screen_angle': self.fix_screen_angle(hs)[-1],
            'fix_euclidean_distance': self.fix_euclidean_distance(hs)[-1],
            'sac_relative_screen_angle': self.sac_relative_screen_angle(hs)[-1],
            'sac_relative_euclidean_distance': self.sac_relative_euclidean_distance(hs)[-1],
            'blink_relative_screen_angle': self.blink_relative_screen_angle(hs)[-1],
            'blink_relative_euclidean_distance': self.blink_relative_euclidean_distance(hs)[-1],
        }}
                    
                    

        return out




class MLP(nn.Module):
    """
    Very simple multi-layer perceptron (also called FFN)
    """

    def __init__(self, input_dim, hidden_dim, output_dim, num_layers):
        super().__init__()
        self.num_layers = num_layers
        h = [hidden_dim] * (num_layers - 1)
        self.layers = nn.ModuleList(nn.Linear(n, k) for n, k in zip([input_dim] + h, h + [output_dim]))

    def forward(self, x):
        for i, layer in enumerate(self.layers):
            x = F.relu(layer(x)) if i < self.num_layers - 1 else layer(x)
        return x


def load_model():
    """
    Load the Unified Scanpath Decoder model for screen polar coordinates.
    
    Args:
        head (str): Either "fixation_only" or "all"
        predicted_error (bool): Whether to include predicted error outputs
    
    Returns:
        DETRtime_scanpath: Loaded model for screen polar coordinates
    """
    # Model parameters from configuration
    model_params = {
        'num_classes': 3,
        'num_queries': 20,
        'backbone': 'inception_time',
        'hidden_dim': 128,
        'timesteps': 500,
        'in_channels': 125,
        'out_channels': 1,
        'kernel_size': 16,
        'nb_filters': 64,
        'use_residual': True,
        'backbone_depth': 3,
        'back_channels': 16,
        'back_layers': 12,
        'nheads': 8,
        'enc_layers': 6,
        'dec_layers': 6,
        'dim_feedforward': 2048,
        'dropout': 0.1,
        'pre_norm': False,
    }
    
    # Create model with specified configuration
    model = UnifiedScanpathDecoder(**model_params)
    
    # Load checkpoint if available
    try:
        ckpt_path = hf_hub_download(
            repo_id="radimurban/unified_scanpath_decoder",
            filename="Unified_Scanpath_Decoder.ckpt"
        )
        checkpoint = torch.load(ckpt_path, map_location="cpu")
        # remove the "net." prefix from state dict keys
        new_state_dict = {}
        for key, value in checkpoint['state_dict'].items():
            if key == "criterion.empty_weight": continue

            if key.startswith("net."):
                new_key = key[4:]  # Remove "net." prefix
            else:
                new_key = key
            
            new_state_dict[new_key] = value

        model.load_state_dict(new_state_dict)
        print(f"Model loaded successfully!")
    except Exception as e:
        print(f"Could not load checkpoint: {e}")
        print("Using randomly initialized model")
    
    model.eval()
    return model

