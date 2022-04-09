import argparse
import os
import pickle
import pprint

from modules.utils import *


def convert_to_im_num(idx, array_num, max_per_array):
    return array_num * max_per_array + idx + 1


def create_feature_matrix(data, batch_size, model):
    data = np.transpose(data, (0, 3, 1, 2))
    print(data.shape)
    feats = []
    bs = batch_size
    start = 0
    end = start + bs
    while start < data.shape[0]:
        batch = convert_array_to_Variable(data[start:end])
        f = model(batch)
        feats.append(f)
        start = end
        end = start + bs
        if start % 50 == 0:
            print("Processed {} ims".format(start))
    feature_matrix = torch.cat(feats, 0)
    feature_matrix = feature_matrix.data.numpy()
    print(feature_matrix.shape)
    return feature_matrix

def create_feature_vector(data):
    model = load_model()
    feats = []
    data = np.transpose(data, (2, 0, 1))
    batch = convert_array_to_Variable(data)
    
    f = model(batch)
    feats.append(f)
    feature_matrix = torch.cat(feats, 0)
    feature_matrix = feature_matrix.data.numpy()
    print(feature_matrix.shape)
    return feature_matrix


def convert_to_dict(feature_matrix, max_per_array):
    feats = {}
    for i in range(feature_matrix.shape[0]):
        key = convert_to_im_num(i, 0, max_per_array)
        feature_vec = feature_matrix[i]
        feats[key] = feature_vec
    return feats


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--npy_path', default='data/test/images_numpy', type=str)
    parser.add_argument('--feat_path', default='data/test/features', type=str)
    parser.add_argument('--batch_size', default=10, type=int)
    opt = parser.parse_args()
    print("-------------------Settings-----------------------")
    pprint.pprint(opt)
    print("-----------------------------------------------------")
    npy_path = opt.npy_path
    feat_path = opt.feat_path
    b_size = opt.batch_size
    model = load_model()
    all_feats = []
    for m in os.listdir(npy_path):
        if ".DS" in m:
            print("Skipping {}".format(m))
        else:
            print("Processing image array {}".format(m))
            m_num = str(m[:-4])
            name = "feat_vec_" + m_num
            data = np.load(os.path.join(npy_path, m))
            feature_matrix = create_feature_matrix(data, b_size, model)
            # np.save(os.path.join(feat_path, name), feature_matrix)
            feats_dict = convert_to_dict(feature_matrix, data.shape[0])
            for k in feats_dict:
                print(feats_dict[k].shape)
                break
            feats_with_names = {str(int(m_num) * 100 + k) + ".jpg": feats_dict[k] for k in feats_dict}
            pickle.dump(feats_with_names, open(os.path.join(feat_path, name + '.in'), "wb"))
            print("Saved feature matrix {}".format(m_num))
            keys = sorted(list(feats_with_names.keys()))
            print("Num keys: {}, first key: {}".format(len(keys), keys[0]))

            #
            # We don't need all feats because wont scale
            # changing the type to .p so that we can send it across stdin
            # making the keys filename so that we don't need to keep mapping it back
            #
            # all_feats.append(feature_matrix)
            # all_feats = np.concatenate(tuple(all_feats), axis=0)
            # print(all_feats.shape)
            # np.save(os.path.join(feat_path, "all_feat_vecs"), all_feats)
            # print("Saved all features in one matrix")
            # feats_dict = convert_to_dict(all_feats)
            # pickle.dump(feats_dict, open(os.path.join(feat_path, "feat_vec_dict.p"), 'wb'))
            # print("Saved feature dictionary")