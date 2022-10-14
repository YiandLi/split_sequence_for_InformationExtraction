# split_sequence_for_InformationExtraction

当输入序列过长时，使用最朴素的方法：裁片，保留所有的片段。

为了保证语义连贯性，使用标点符号进行 split，同时保存时每一个样本也要保存对应的 spo 三元组信息，对应的 entity index 就需要更新。
