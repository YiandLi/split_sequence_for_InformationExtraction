import json
import re


def train_generator():
    fr = open('data/bdci/train_bdci.json').readlines()
    fw = open('data/bdci/train.json', 'w', encoding='utf8')
    
    arr_all = []
    
    for i in fr:
        i = i.strip()
        if i == "":
            continue
        
        dic_single = {}
        arr_single = []
        
        data = json.loads(i)
        id = data['ID']
        text = data['text']
        spo_list = data['spo_list']
        
        # id_input = int(id.replace('AT', '').lstrip('0'))
        dic_single['id'] = id
        dic_single['text'] = text
        dic_single['spos'] = []
        
        if text in arr_all:
            continue
        
        if len(text) > 200:
            """
            如果超过预定义长度，则按照标点切割 text，并且不断拼接，直到超过最大长度
            """
            for spo in spo_list:
                h = spo['h']
                t = spo['t']
                relation = spo['relation']
                line = [(h['pos'][0], h['pos'][1], h['name']), relation, (t['pos'][0], t['pos'][1], t['name'])]
                arr_single.append(line)
            
            # dict_all[text] = arr_single
            spos = sorted(arr_single)
            # 按照预定义 cut_pattern 进行切割
            split_blocks = cut_pattern.split(text)
            split_blocks.append("")
            # 切出来后是 sub_sequence + "," 的 形式，所以这里进行融合
            split_blocks = ["".join(i) for i in zip(split_blocks[0::2], split_blocks[1::2])]
            current_text = ""  # 用来防止当前需要进行 concat 的 sub_sequence
            total_blocks = []
            
            for block in split_blocks:
                if len(current_text + block) > 200:
                    total_blocks.append(current_text)
                    current_text = block
                else:
                    current_text += block
            
            if len(current_text) > 0:
                total_blocks.append(current_text)  # 所有 切割+concat 后，长度不超过 200 的句子都被放到 total_blocks
            
            start_idx = 0
            end_idx = 0
            for t_idx, block_text in enumerate(total_blocks):
                
                end_idx += len(block_text)
                new_spos = []
                for spo in spos:
                    
                    h_sidx, h_eidx, h_name = spo[0]
                    t_sidx, t_eidx, t_name = spo[2]
                    
                    if start_idx <= h_eidx < end_idx and start_idx <= t_eidx <= end_idx:  # 选出这一区间的 spo 元祖信息
                        new_spos.append(spo)
                
                if t_idx == 0:
                    line = {"id": id, "text": block_text, "spos": new_spos}
                    arr_all.append(line)
                
                else:
                    new_spos2 = []
                    for spo in new_spos:
                        h_sidx, h_eidx, h_name = spo[0]
                        relation = spo[1]
                        t_sidx, t_eidx, t_name = spo[2]
                        tmp = []
                        tmp.append((h_sidx - start_idx, h_eidx - start_idx, h_name))
                        tmp.append(relation)
                        tmp.append((t_sidx - start_idx, t_eidx - start_idx, t_name))
                        new_spos2.append(tmp)
                    
                    line = {"id": id, "text": block_text, "spos": new_spos2}
                    arr_all.append(line)
                start_idx += end_idx
        
        else:
            for spo in spo_list:
                h = spo['h']
                t = spo['t']
                relation = spo['relation']
                
                arr_h = []
                arr_h.append(h['pos'][0])
                arr_h.append(h['pos'][1])
                arr_h.append(h['name'])
                
                arr_t = []
                arr_t.append(t['pos'][0])
                arr_t.append(t['pos'][1])
                arr_t.append(t['name'])
                
                arr_spo = []
                arr_spo.append(arr_h)
                arr_spo.append(relation)
                arr_spo.append(arr_t)
                dic_single['spos'].append(arr_spo)
            
            arr_all.append(dic_single)
    
    fw.writelines(json.dumps(arr_all, ensure_ascii=False, indent=2))


def _test_generator():
    fr = open('data/bdci/evalA.json', 'r', encoding='utf8').readlines()
    fw = open('data/bdci/test.json', 'w', encoding='utf8')
    
    datas = []
    for case in fr:
        case_data = json.loads(case)
        idx = case_data['ID']
        txt = case_data['text']
        if len(txt) > 200:
            split_blocks = cut_pattern.split(txt)
            split_blocks.append("")
            
            split_blocks = ["".join(i) for i in zip(split_blocks[0::2], split_blocks[1::2])]
            current_text = ""
            total_blocks = []
            for block in split_blocks:
                if len(current_text + block) > 200:
                    total_blocks.append(current_text)
                    current_text = block
                else:
                    current_text += block
            
            if len(current_text) > 0:
                total_blocks.append(current_text)
            
            for sub_idx, block in enumerate(total_blocks):
                line = {"id": str(idx) + "_{}".format(sub_idx), "text": block}
                datas.append(line)
        else:
            line = {"id": str(idx), "text": txt}
            datas.append(line)
    
    json.dump(datas, fw, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    cut_pattern = re.compile(r'([，。！？、])')
    # train_generator()
    _test_generator()
