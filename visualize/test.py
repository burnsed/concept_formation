import random
import json
import pprint
import argparse

import concept_formation.datasets as ds
from concept_formation.trestle import TrestleTree
from concept_formation.preprocessor import ObjectVariablizer


def output_json(file="forest_fire",size=100,prune=True,seed=50):
    random.seed(seed)
    if file == "forest_fires":
        instances = ds.load_forest_fires()
        variables = False
    elif file == "congressional_voting":
        instances = ds.load_congressional_voting()
        variables = False
    elif file == "iris":
        instances = ds.load_iris()
        variables = False
    elif file == "mushroom":
        instances = ds.load_mushroom()
        variables = False
    elif file == "rb_com_11":
        instances = ds.load_rb_com_11()
        variables = True
    elif file == "rb_s_07":
        instances = ds.load_rb_s_07()
        variables = True
    elif file == "rb_s_13":
        instances = ds.load_rb_s_13()
        variables = True
    elif file == "rb_wb_03":
        instances = ds.load_rb_wb_03()
        variables = True 

    instances = ds.load_forest_fires()
    variables = False

    random.shuffle(instances)
    pprint.pprint(instances[0])
    instances = instances[:size]
    print(len(instances))

    if variables:
        variablizer = ObjectVariablizer()
        instances = [variablizer.transform(t) for t in instances]

    tree = TrestleTree()
    tree.fit(instances)

    with open('output.js','w') as out:
        out.write("var output = ")
        out.write(json.dumps(tree.root.output_json(prune)))
        out.write(";")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Output example files for testing Viz.')
    parser.add_argument('file',choices=["forest_fires","congressional_voting","iris","mushroom","rb_com_11","rb_s_07","rb_s_13"],help="which example dataset to use")
    parser.add_argument('-size',type=int,default=100,help='how many instances to use')
    parser.add_argument('-prune',action='store_true',help='whether to output the tree with pruning applied.')
    parser.add_argument('-seed',type=int,default=50,help='seed to use when shuffling instances for training.')

    args = parser.parse_args()

    output_json(args.file,args.size,args.prune,args.seed)