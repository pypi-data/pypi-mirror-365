# RRPad
ReplicationReflectionPad combines ReplicationPad and ReflectionPad to prevent errors from being reported due to small input sizes when using non-constant padding types.

## Install
```bash
pip install RRPad
```

## Use
```python
from RRPad import ReplicationReflectionPad1d,ReplicationReflectionPad2d
...
pad=ReplicationReflectionPad1d(paddingSize)
input=torch.randn((1,2,3))
output=pad(input)
```

## HomePage
<https://github.com/PsycheHalo/RRPad/>
