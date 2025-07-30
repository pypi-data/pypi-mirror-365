#!/usr/bin/env python
# -*- coding: utf-8 -*-

from transformers import AutoTokenizer

from hakkero.dataset.mixed_dataset import get_dataset
from hakkero.dataset import PackPadLoader

if __name__ == "__main__":
    config = {
        "pt": {
            "group": "en",
            "name": "pt",
            "epoch": 1,
            "path": f"/Users/qinluo/work/repo/hakkero-dataloader/tests/data/pt.packed",
            "strategy": {"st_segment": "naive", "st_tokenize": "legacy"},
            "weight": 1.0,
        }
    }

    model_path = "/Users/qinluo/work/models/moonshotai/Moonlight-16B-A3B"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    max_length = 4096
    batch_size = 2
    n_workers = 2
    shift = False

    ds = get_dataset(
        config,
        tokenizer,
        num_epochs=1,
        max_length=max_length,
        homogeneous=True,
        seed=-1,
        rank=0,
        world_size=1,
        n_workers=n_workers,
        shift=False,
    )

    dataloader = PackPadLoader(
        ds, batch_size=batch_size, padding_id=tokenizer.pad_token_id, unpad=True, bos_id=tokenizer.bos_id, eos_id=tokenizer.eos_id
    )

    total_samples = 0
    for step, batch in enumerate(dataloader, start=1):
        total_samples += batch["n_samples"]
        print(f"step={step}, samples={batch['n_samples']}, n_tokens={batch['n_tokens']}, total_samples={total_samples}")
        ds.track(batch["stats"])
