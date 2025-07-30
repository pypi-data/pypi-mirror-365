import argparse
import importlib.resources
import os


def argsParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_random_smiles", help="random smiles", type=int, default=10)
    parser.add_argument("--lr", help="learning rate", type=float, default=0.001)
    parser.add_argument("--scheduler_gamma", help="weight_decay", type=float, default=0.995)
    parser.add_argument("--weight_decay", help="weight_decay", type=float, default=1e-05)
    parser.add_argument("--epoch", help="epoch", type=int, default=1000)
    parser.add_argument("--ngpu", help="number of gpu", type=int, default=1)
    parser.add_argument("--batch_size", help="batch_size", type=int, default=32)
    parser.add_argument("--atom_feature_atom_size", help="atom size", type=str2bool, default=True)
    parser.add_argument("--atom_feature_element", help="atom element", type=str2bool, default=False)
    parser.add_argument("--atom_feature_electronegativity", help="atom electronegativity", type=str2bool, default=True)
    parser.add_argument("--atom_feature_hardness", help="atom hardness", type=str2bool, default=True)
    parser.add_argument("--atom_feature_hybridization", help="atom hybridization", type=str2bool, default=True)
    parser.add_argument("--atom_feature_aromaticity", help="atom aromaticity", type=str2bool, default=True)
    parser.add_argument("--atom_feature_number_of_rings", help="number of rings", type=str2bool, default=False)
    parser.add_argument("--atom_feature_ring_size", help="atom ring size", type=str2bool, default=True)
    parser.add_argument("--atom_feature_number_of_Hs", help="number of hydrogen(s) bound", type=str2bool, default=True)
    parser.add_argument("--atom_feature_formal_charge", help="number of hydrogen(s) bound", type=str2bool, default=True)
    parser.add_argument("--bond_feature_bond_order", help="bond order", type=str2bool, default=True)
    parser.add_argument("--bond_feature_conjugation", help="bond conjugation", type=str2bool, default=True)
    parser.add_argument("--bond_feature_charge_conjugation", help="bond conjugation with charge", type=str2bool, default=True)
    parser.add_argument("--bond_feature_polarization", help="bond polarization", type=str2bool, default=True)
    parser.add_argument("--bond_feature_focused", help="bond features focused", type=str2bool, default=False)
    parser.add_argument("--acid_or_base", help="acid only, base only or both", type=str, default="base")
    parser.add_argument("--num_workers", help="number of workers", type=int, default=0)
    parser.add_argument("--n_graph_layers", help="number of GNN layers", type=int, default=4)
    parser.add_argument("--embedding_size", help="dimension of embedding", type=int, default=128)
    parser.add_argument("--mask_size", help="dimension of local environment", type=int, default=4)
    parser.add_argument("--n_FC_layers", help="number of FC layers", type=int, default=2)
    parser.add_argument("--model_dense_neurons", help="dimension of FC layers", type=int, default=448)
    parser.add_argument("--model_attention_heads", help="model attention heads", type=int, default=4)
    parser.add_argument("--dropout_rate", help="dropout_rate", type=float, default=0.1)
    parser.add_argument("--GATv2Conv_Or_Other", help="GNN model", type=str, default="GATv2Conv")
    parser.add_argument("--mode", help="train, test, infer, pH", type=str, default="usage")
    parser.add_argument("--hyperopt_max_evals", help="maximum number of evaluations", type=int, default=50)
    parser.add_argument("--hyperopt_convergence", help="max number of epoch with no improvement", type=int, default=50)
    parser.add_argument("--hyperopt_max_increase", help="threshold above min loss", type=float, default=0.10)

    parser.add_argument("--verbose", help="amount of data output", type=int, default=0)
    parser.add_argument("--data_path", help="path to data folder", type=str, default='..//Datasets//')
    parser.add_argument("--save_dir", help="save directory of model parameter", type=str, default='./saved_models/')
    parser.add_argument("--output", help="output file prefix", type=str, default='output/')
    parser.add_argument("--input", help="input file prefix", type=str, default='none')
    parser.add_argument("--train_data", help="train data", type=str, default='Complete_Set.csv')
    parser.add_argument("--test_data", help="test data", type=str, default='Complete_Set.csv')
    parser.add_argument("--train_pickled", help="train pickled", type=str, default='pickled_data/train_pickled.pkl')
    parser.add_argument("--test_pickled", help="test pickled", type=str, default='pickled_data/test_pickled.pkl')
    parser.add_argument("--carbons_included", help="including carbon ionization center", type=str2bool, default=True)
    parser.add_argument("--model_dir", help="directory where model is", type=str, default='../Model/')
    parser.add_argument("--model_name", help="model file name", type=str, default='model_4-4.pth')
    parser.add_argument("--infer_pickled", help="test3 pickled", type=str, default='..//Datasets//pickled_data//infer_pickled.pkl')
    parser.add_argument("--pH", help="pH", type=float, default=7.4)
    parser.add_argument("--restart", help="restart", type=str, default='none')
    parser.add_argument("--load_model", help="restart", type=str, default='none')
    parser.add_argument("--model_txt_file", help="restart", type=str, default='none')
    parser.add_argument("--seed", help="seed", type=int, default='42')
    parser.add_argument("--node_feature_size", help="number of features for nodes", type=int, default=0)
    parser.add_argument("--edge_feature_size", help="number of features for edges", type=int, default=0)

    args = parser.parse_args()

    # If the defaults are being used (user did NOT override model_dir/name), use package resource
    if (args.model_dir == '../Model/' and args.model_name == 'model_4-4.pth'):
        with importlib.resources.path("pka_predictor.Model", "model_4-4.pth") as model_path:
            args.model_dir = os.path.dirname(str(model_path)) + os.sep
            args.model_name = os.path.basename(str(model_path))
    
    print('|----------------------------------------------------------------------------------------------------------------------------|')
    print('| pKa predictor                                                                                                              |')
    print('| Jerome Genzling, Ziling Luo, Benjamin Weiser, Nic Moitessier                                                               |')
    print('| Department of Chemistry, McGill University, Montreal, QC, Canada                                                           |')
    print('|----------------------------------------------------------------------------------------------------------------------------|')
    print('| Parameters used:                                                                                                           |')
    print('| --mode (train, hyperopt, test, infer or pH):                       %-55s |' % args.mode)
    print('| --verbose (level of output):                                       %-55s |' % args.verbose)
    if args.mode == 'train' or args.mode == 'hyperopt':
        print('| --n_random_smiles (number of random smiles)                        %-55.0f |' % args.n_random_smiles)
        print('| --GATv2Conv_Or_Other (GATv2Conv or TransformerConv):               %-55.6f |' % args.lr)
        print('| --lr (learning rate):                                              %-55.6f |' % args.lr)
        print('| --weight_decay (weight decay):                                     %-55.6f |' % args.weight_decay)
        print('| --scheduler_gamma (gamma for scheduler):                           %-55.6f |' % args.scheduler_gamma)
        print('| --epoch (number of epochs):                                        %-55.0f |' % args.epoch)
        print('| --ngpu (number of gpu):                                            %-55.0f |' % args.ngpu)
        print('| --batch_size (batch_size):                                         %-55.0f |' % args.batch_size)
        print('| --atom_feature_element (atom element):                             %-55s |' % args.atom_feature_element)
        print('| --atom_feature_atom_size (atom size):                              %-55s |' % args.atom_feature_atom_size)
        print('| --atom_feature_electronegativity (electronegativity):              %-55s |' % args.atom_feature_electronegativity)
        print('| --atom_feature_hardness (hardness):                                %-55s |' % args.atom_feature_hardness)
        print('| --atom_feature_hybridization (hybridization):                      %-55s |' % args.atom_feature_hybridization)
        print('| --atom_feature_aromaticity (aromaticity):                          %-55s |' % args.atom_feature_aromaticity)

        print('| --atom_feature_number_of_rings (number of rings):                  %-55s |' % args.atom_feature_number_of_rings)
        print('| --atom_feature_ring_size (ring size):                              %-55s |' % args.atom_feature_ring_size)
        print('| --atom_feature_number_of_Hs (number of Hs bound):                  %-55s |' % args.atom_feature_number_of_Hs)
        print('| --atom_feature_formal_charge (formal charge):                      %-55s |' % args.atom_feature_formal_charge)
        print('| --bond_feature_bond_order (bond order):                            %-55s |' % args.bond_feature_bond_order)
        print('| --bond_feature_conjugation (bond conjugation):                     %-55s |' % args.bond_feature_conjugation)
        print('| --bond_feature_charge_conjugation (charge and conjugation):        %-55s |' % args.bond_feature_charge_conjugation)
        print('| --bond_feature_polarization (bond polarization):                   %-55s |' % args.bond_feature_polarization)
        print('| --bond_feature_focused (focusing on conjugation)                   %-55s |' % args.bond_feature_focused)

        print('| --acid_or_base (features included):                                %-55s |' % args.acid_or_base)
        print('| --num_workers (number of workers for multiple CPU usage):          %-55.0f |' % args.num_workers)
        print('| --n_graph_layer (number of GNN layers):                            %-55.0f |' % args.n_graph_layers)
        print('| --embedding_size (dimension of embedding after GNN layers):        %-55.0f |' % args.embedding_size)
        print('| --mask_size (dimension of local environment):                      %-55.0f |' % args.mask_size)
        print('| --n_FC_layer (number of fully connected layers):                   %-55.0f |' % args.n_FC_layers)
        print('| --model_dense_neurons (dimension of the fully connected layers):   %-55.0f |' % args.model_dense_neurons)
        print('| --model_attention_heads (multi head attention)                     %-55.0f |' % args.model_attention_heads)
        print('| --dropout_rate (dropout_rate):                                     %-55.2f |' % args.dropout_rate)
        print('| --data_path (path to the data folder - csv format):                %-55s |' % args.data_path)
        print('| --save_dir (directory where model parameters will be saved):       %-55s |' % args.save_dir)
        print('| --output (output file prefix):                                     %-55s |' % args.output)
        print('| --model_name (model file name):                                    %-55s |' % args.model_name)
        print('| --train_data (data of the training set):                           %-55s |' % args.train_data)
        print('| --test_data (data of the testing set):                             %-55s |' % args.test_data)
        print('| --train_pickled (path to the pickled training set):                %-55s |' % args.train_pickled)
        print('| --test_pickled (path to the pickled testing set):                  %-55s |' % args.test_pickled)
        print('| --restart (model from which to restart training):                  %-55s |' % args.restart)
        print('| --seed (seed value for randomizer):                                %-55.0f |' % args.seed)

    if args.mode == 'train' or args.mode == 'hyperopt':
        print('| --hyperopt_max_evals (max evaluations for hyperopt):               %-55.0f |' % args.hyperopt_max_evals)
        print('| --hyperopt_convergence (max number of epochs with no improvement)  %-55.0f |' % args.hyperopt_convergence)
        print('| --hyperopt_max_increase (upper threshold after 100 epochs)         %-55.3f |' % args.hyperopt_max_increase)

    if args.mode == 'test' or args.mode == 'infer' or args.mode == 'pH':
        print('| --data_path (path to the data folder):                             %-55s |' % args.data_path)
        print('| --input (input file name):                                         %-55s |' % args.input)
        print('| --model_dir (directory where model is):                            %-55s |' % args.model_dir)
        print('| --model_name (model file name):                                    %-55s |' % args.model_name)
        print('| --output (output file name):                                       %-55s |' % args.output)
        print('| --infer_pickled (path to the pickled inference set):               %-55s |' % args.infer_pickled)

    if args.mode == "pH":
        print('| --pH (pH of the most likely protonation state):                    %-55.1f |' % args.pH)

    print('|----------------------------------------------------------------------------------------------------------------------------|', flush=True)
    return args


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
