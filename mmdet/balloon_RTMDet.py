# config file for balloon dataset
# in reference to mmdet/configs/rtmdet/rtmdet_tiny_8xb32-300e_coco.py
# and mmdet/configs/rtmdet/rtmdet_l_8xb32-300e_coco.py

_base_ = "./configs/rtmdet/rtmdet_tiny_8xb32-300e_coco.py"

# data_root = "."
data_root = "./data/balloon/"


# in reference to https://github.com/CrabBoss-lab/openmmlab-Camp/blob/master/03-mmdetection-task/mmdetection/balloon_dataset/balloon_rtmdet.py
metainfo = dict(
    classes=('balloon', ),
    palette=[(220,20,60),]
)
num_classes = len(metainfo['classes'])

max_epochs = 200
train_batch_size_per_gpu = 32
train_num_workers = 8

val_batch_size_per_gpu = 12
val_num_workers = 6

# RTMDet consists of 2 training stage
num_epochs_stage2 = 5
base_lr = 0.04 * train_batch_size_per_gpu / (32*8)

# pretrain weights
# you can find this ./mmdet/configs/rtmdet/metafile.yml
load_from = 'https://download.openmmlab.com/mmdetection/v3.0/rtmdet/rtmdet_tiny_8xb32-300e_coco/rtmdet_tiny_8xb32-300e_coco_20220902_112414-78e30dcc.pth'  # noqa

# fix model backbone
model = dict(
    backbone=dict(frozen_stages=4),
    bbox_head=dict(dict(num_classes=num_classes)),
)

train_dataloader = dict(
    batch_size=train_batch_size_per_gpu,
    num_workers=train_num_workers,
    pin_memory=True,
    dataset=dict(
        data_root=data_root,
        metainfo=metainfo,
        ann_file='train/balloon_train.json',
        data_prefix=dict(img='train/'),
    ),
)

val_dataloader = dict(
    batch_size=val_batch_size_per_gpu,
    num_workers=val_num_workers,
    # pin_memory=True,
    dataset=dict(
        data_root=data_root,
        metainfo=metainfo,
        ann_file='val/balloon_val.json',
        data_prefix=dict(img='val/'),
    ),
)

test_dataloader = val_dataloader


param_scheduler = [
    dict(
        type='LinearLR', start_factor=0.00001, by_epoch=False, begin=0, end=30),
    # dict(
    #     type='MultiStepLR',
    #     begin=0,
    #     end=epochs_multilr,
    #     by_epoch=True,
    #     milestones=milestones_multilr,
    #     gamma=0.1),
    dict(
        type='CosineAnnealingLR',
        eta_min=base_lr * 0.05,
        begin=max_epochs // 2,  # max_epoch 也改变了
        end=max_epochs,
        T_max=max_epochs // 2,
        by_epoch=True,
        convert_to_iter_based=True
    ),
]

# optimizer
optim_wrapper = dict(
    type='OptimWrapper',
    optimizer=dict(type='SGD', lr=base_lr, momentum=0.9, weight_decay=0.0001))

_base_.custom_hooks[1].switch_epoch = max_epochs - num_epochs_stage2

val_evaluator = dict(ann_file=data_root + './val/balloon_val.json')
test_evaluator = val_evaluator


default_hooks = dict(
    logger=dict(type='LoggerHook', interval=5),
    checkpoint=dict(type='CheckpointHook', interval=5, save_best='auto'),
)
train_cfg = dict(max_epochs=max_epochs, val_interval=10)
