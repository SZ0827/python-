import os
import json
from py2neo import Graph, Node
import time
import webbrowser



class MedicalGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'zhongyao/fangji_data.json')
        self.g = Graph("http://localhost:7474/", auth=("neo4j", "j20010201"), name='neo4j')

    '''读取文件'''

    def read_nodes(self):
        # 共6类节点
        fangjis = []  # 方剂
        catagorys = []  # 分类
        origins = []  # 出处
        elements = []  # 组成
        uses = []  # 用法
        functions = []  # 功效

        fangji_infos = []  # 方剂信息
        # 构建节点实体关系
        rels_catagory = []  # 方剂－分类关系
        rels_origin = []  # 方剂-出处关系
        rels_element = []  # 方剂-组成关系
        rels_use = []  # 方剂-用法关系
        rels_function = []  # 方剂-功效关系

        count = 0
        #准备数据
        for data in open(self.data_path, encoding='utf-8'):
            fangji_info = {}
            count += 1
            data_json = json.loads(data)  # json中一行的数据
            fangji = data_json['name']
            fangji_info['name'] = fangji
            fangjis.append(fangji)
            fangji_info['origin'] = ''
            fangji_info['catagory'] = ''
            fangji_info['element'] = ''
            fangji_info['use'] = ''
            fangji_info['function'] = ''
            if 'catagory' in data_json:
                catagorys = data_json['catagory'] + catagorys
                fangji_info['catagory'] = data_json['catagory']
                for catagory in data_json['catagory']:
                    rels_catagory.append([fangji, catagory])
            if 'origin' in data_json:
                origins += data_json['origin']
                fangji_info['origin'] = data_json['origin']
                for origin in data_json['origin']:
                    rels_origin.append([fangji, origin])
            if 'use' in data_json:
                uses += data_json['use']
                fangji_info['use'] = data_json['use']
                for use in data_json['use']:
                    rels_use.append([fangji, use])
            if 'function' in data_json:
                functions += data_json['function']
                fangji_info['function'] = data_json['function']
                for function in data_json['function']:
                    rels_function.append([fangji, function])
            if 'element' in data_json:
                elements += data_json['element']
                fangji_info['element'] = data_json['element']
                for element in data_json['element']:
                    rels_element.append([fangji, element])
            fangji_infos.append(fangji_info)
        return set(catagorys), set(origins), set(elements), set(uses), set(functions),set(fangjis),fangji_infos,rels_catagory,rels_origin,rels_element,rels_use,rels_function

    def create_node(self, label, nodes):
        count = 0
        # set为了对nodes进行去重处理
        for node_name in set(nodes):
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
        return

    def create_fangji_nodes(self, fangji_infos):
        count = 0
        for fangji_info1 in fangji_infos:
            node = Node("fangji", name=fangji_info1['name'], catagory=fangji_info1['catagory'],origin=fangji_info1['origin'],element=fangji_info1['element'], users=fangji_info1['use'],function=fangji_info1['function'])
            self.g.create(node)
            count += 1
        return

    def create_graphnodes(self):
        Catagorys,Origins,Elements,Users,Functions,Fangjis,fangji_infos,rels_catagory,rels_origin,rels_element,rels_use,rels_function=self.read_nodes()
        #self.create_fangji_nodes(fangji_infos)
        self.create_node('catagory', Catagorys)
        print("方剂类别节点创建完成,一共" + str(len(Catagorys)) + '种')
        self.create_node('origin', Origins)
        print("方剂出处节点创建完成,一共" + str(len(Origins)) + '种')
        self.create_node('element', Elements)
        print("方剂组成节点创建完成,一共" + str(len(Elements)) + '种')
        self.create_node('user', Users)
        print("方剂使用节点创建完成,一共" + str(len(Users)) + '种')
        self.create_node('function',Functions)
        print("方剂功效节点创建完成,一共" + str(len(Fangjis)) + '种')
       # self.create_node('fangjis', Fangjis)
        print("全部节点创建完成")
        return

    def creat_graphrels(self):
        Catagorys, Origins, Elements, Users, Functions, Fangjis, fangji_infos, rels_catagory, rels_origin, rels_element \
            , rels_use, rels_function = self.read_nodes()
        self.create_fangji_nodes(fangji_infos)
        self.create_relationship('catagory', 'fangji', rels_catagory, 'fangji_catagory', '方剂的类别')
        self.create_relationship('origin', 'fangji', rels_origin, 'fangji_origin', '方剂的出处')
        self.create_relationship('element', 'fangji', rels_element, 'fangji_element', '方剂的组成')
        self.create_relationship('user', 'fangji', rels_use, 'fangji_use', '方剂的使用')
        self.create_relationship('function', 'fangji', rels_function, 'fangji_function', '方剂的功效')

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        for edge in edges:
            q = edge[0]
            p = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
            except Exception as e:
                print(e)
        print(rel_name + "关系以构建完毕，一共" + str(len(edges)) + "种")
        return
    def open(self):
        chromePath = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chromePath))
        webbrowser.get('chrome').open('http://localhost:63342/0-1中医药图谱/templates/display.html', new=1, autoraise=True)
        time.sleep(5)


if __name__ == '__main__':
    handler = MedicalGraph()
    print("正在创建图谱结点中请等待...........")
    handler.create_graphnodes()
    print("正在构建图谱节点关系中请等待........")
    handler.creat_graphrels()
    handler.open()

