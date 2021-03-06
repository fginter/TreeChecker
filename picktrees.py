import os
import sys
import jinja2
import random


def read_conll(inp,maxsent=0):
    """ Read conll format file and yield one sentence at a time as a list of lists of columns. If inp is a string it will be interpreted as fi
lename, otherwise as open file for reading in unicode"""
    count=0
    sent=[]
    comments=[]
    for lineno,line in enumerate(inp):
        line=line.strip()
        if not line:
            if sent:
                count+=1
                yield sent, comments
                if maxsent!=0 and count>=maxsent:
                    break
                sent=[]
                comments=[]
        elif line.startswith(u"#"):
            if sent:
                raise ValueError("Missing newline after sentence")
            comments.append(line)
            continue
        else:
            sent.append(line.split(u"\t")+[lineno+1])
    else:
        if sent:
            yield sent, comments
import re
nre=re.compile("[^a-zA-Z0-9-]")
linere=re.compile(r"^context \| (L|R), (.*?) with \((.*), (.*)\) at \(([0-9]+), ([0-9]+)\)$")
linerelemma=re.compile(r"^context \| (L|R), (.*?) at \(([0-9]+), ([0-9]+)\)$")
ID,FORM,LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS,MISC=range(10)

l=jinja2.FileSystemLoader("templates")
it=l.load(jinja2.Environment(),"index_template.html")
lt=l.load(jinja2.Environment(),"list_template.html")

def print_block(rnd_idx,fname,block_trees,left,right,args,random_sample=False):
    # prints a block and return info needed in index page

    sorted_trees=sorted(block_trees.items(),key=lambda itm: len(itm[1]))

    # if random_sample:
    limited_trees=[]
    for dtype,all_trees in sorted_trees:
        limited_trees.append((dtype,random.sample(all_trees,min(args.max_trees,len(all_trees)))))
    sorted_trees=limited_trees
    

    with open(fname+".conllu","wt") as f: # this just prints dtype...
        print(u"\n".join(dtype for dtype,v in sorted_trees),file=f)

    html=it.render(trees=sorted_trees,title=fname,collection=args.collection)
    with open(fname+".html","wt") as f:
        print(html,file=f)

    # index page
    total=sum(len(v) for dtype,v in sorted_trees)
    typecount=len(sorted_trees)
    types=", ".join(sorted(dtype for dtype,v in sorted_trees))
    link=os.path.basename(fname+".html")
    if len(left)>15:
        left=left[:12]+"..."
    if len(right)>15:
        right=right[:12]+"..."
    if len(types)>30:
        types=types[:27]+"..."
        
    return ((rnd_idx,total,typecount,types,left,right),link)


def print_trees(inp,line2treeidx,trees,args,random_sample=False):

    files=[] # total, typecount, types, left, right, link
    
    tree_counter=0
    all_blocks=[]
    for line in inp:
        line=line.rstrip()
        if not line: # store last block
            # fname, block_trees
            all_blocks.append((fname,block_trees,left,right))
            
        elif line[0].isspace():
            #context | L, xcomp:ds with (ylennettiin, ylipäälliköksi) at (190794, 190800)
            match=linere.match(line.strip())
            if match:
                lr,dtype,w1,w2,l1,l2=match.groups()
            else:
                match=linerelemma.match(line.strip())
                lr,dtype,l1,l2=match.groups()
                w1=None
                w2=None
            l1,l2=int(l1),int(l2)
            tree,comments=trees[line2treeidx[l1]]
            assert tree==trees[line2treeidx[l2]][0]
            treebeg=tree[0][-1]
            gov=l1-treebeg
            dep=l2-treebeg
            assert w1 is None or tree[gov][FORM]==w1
            assert w2 is None or tree[dep][FORM]==w2
            if lr=="R":
                gov,dep=dep,gov
                w1,w2=w2,w1
            if not ((tree[dep][HEAD]==tree[gov][ID] and tree[dep][DEPREL]==dtype) or (tree[gov][ID]+":"+dtype in tree[dep][DEPS])):
                print(".",flush=True)
                print(line)
                print("\n".join("\t".join(str(c) for c in cols) for cols in tree))
                print()
                print()
            # # visual-style 24 16 advmod     color:gray
            conllu="\n".join(("# "+line,"# visual-style\t{}\tbgColor:red".format(tree[gov][ID]),\
                  "# visual-style\t{}\tbgColor:red".format(tree[dep][ID]),\
                    "# visual-style\t{} {} {}\tcolor:red".format(tree[gov][ID],tree[dep][ID],tree[dep][DEPREL]),\
                    "\n".join("\t".join(cols[:-1]) for cols in tree),""))
            tree_id=fname.split("/")[-1]+"_"+str(tree_counter)
            # TODO: add here necessary metadata
            tree_meta="gov_form:{g}, dep_form:{d}, deprel:{dtype}, left:{l}, right:{r}".format(g=tree[gov][FORM],d=tree[dep][FORM],dtype=tree[dep][DEPREL],l=left.replace('"',''),r=right.replace('"',''))
            block_trees.setdefault(dtype,[]).append((conllu,tree_id,tree_meta))
            tree_counter+=1
            
        else:
            #new block
            left,right=line.split(", ")
            fname=args.out+"/"+nre.sub("_",line.replace(", ","------"))
            block_trees={} #dtype -> trees
            tree_counter=0

    # now we have all blocks, take random sample, or print all
    # if random_sample:
    #     my_sample=random.sample(all_blocks,min(100,len(all_blocks)))
    # else:
    #     my_sample=all_blocks
    random.shuffle(all_blocks)
    for rnd_idx,(fname,block_trees,left,right) in enumerate(all_blocks):
        index_info=print_block(rnd_idx,fname,block_trees,left,right,args,random_sample=random_sample)
        files.append(index_info)

    with open(args.out+"/index.html","wt") as f:
        print(lt.render(files=files),file=f)
        

if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='gizmo')
    parser.add_argument('--conllu', required=True, help='Input conllu')
    parser.add_argument('--ctx', required=True, help='Input contexts')
    parser.add_argument('--collection', required=True, help='Collection name for flask_shelve')
    parser.add_argument('--out', required=True, help='outdir')
    parser.add_argument('--random', action='store_true', default=False, help='Take random sample')
    parser.add_argument('--max-trees', default=50, type=int, help='Maximum number of trees per dependency type shown on the page')
    
    args = parser.parse_args()

    os.system("mkdir -p "+args.out)
#    os.system("cp -r js css fonts "+args.out)
    os.system("cp -r static "+args.out)
#    os.system("cp flask_shelve.js "+args.out)

    line2treeidx={}
    trees=list(read_conll(open(args.conllu)))
    for treeidx,(tree,comments) in enumerate(trees):
        for cols in tree:
            line2treeidx[cols[-1]]=treeidx
    print_trees(open(args.ctx),line2treeidx,trees,args,random_sample=args.random)



    
