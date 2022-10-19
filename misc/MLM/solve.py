from transformers import BertConfig, BertForMaskedLM, BertTokenizer
import numpy as np
import torch
import pickle

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

def load_layers_to_weights(layers):
  """
  Function that converts list of numpy flat arrays(layers) to a 
  model based on model dimensions (model_dim)
  """

  with torch.no_grad():
    model = BertForMaskedLM(config=BertConfig())
    model_dim = get_model_dim(model) 
    for layer, param in enumerate(model.parameters()):
      if len(model_dim[layer]) == 2 :
        param.data = torch.tensor(layers[layer].reshape(model_dim[layer][0], model_dim[layer][1])).data
      else:
        param.data = torch.tensor(layers[layer]).data
  return model

def get_model_dim(model):
  """
  Function that return model dimensions of each layer
  in a list of lists (model_param)
  
  """
  model_param = []
  for param in model.parameters():
    model_param.append(list(param.shape))
  return model_param

def inference(model, flag):
  """
  Test the performance of the model, place {tokenizer.mask_token}
  anywhere where you want to get the prediction
  
  """

  sequence = flag+tokenizer.mask_token
  input_ids = tokenizer.encode(sequence, return_tensors="pt")
  mask_token_index = torch.where(input_ids == tokenizer.mask_token_id)[1]

  token_logits = model(input_ids)[0]
  mask_token_logits = token_logits[0, mask_token_index, :]
  mask_token_logits = torch.softmax(mask_token_logits, dim=1)

  top_token = torch.topk(mask_token_logits, 1, dim=1).indices[0].tolist()[0]
  return sequence.replace(tokenizer.mask_token, tokenizer.decode([top_token]))

def solve():
    layers = [] 
    for i in range(202):
      layers.append(pickle.load(open(f"extracted_layers/layer{i}.pkl","rb")))

    model = load_layers_to_weights(layers)
    
    flag = "CyberErudites{" 
    while "}" not in flag :
        flag = inference(model, flag).replace("#","")
    print(f"Flag is : {flag}")

solve()