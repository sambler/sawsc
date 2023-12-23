
This is **SawsC**

Pronounced "Saucy"

SawsC is Shane's AWS Configurator, which is a tkinter GUI that uses boto3 to assist developing and maintaining AWS resources.

At this stage it mostly just simplifies ec2 control.

install into home bin

```sh
python -m pip install -e .
```

run as gui
```sh
sawscui
```

run as cli
```sh
sawsc --help
```

You can run `sawsc` and get a list of known ec2 instances (same as using the -l option). `sawsc i-012301230123` will startup the instance id, or you can `sawsc -r` and then choose the instance from the list.

Currently you can setup ssh key paths using the gui. For the cli you can manually enter then into the config file, which is a json dict with `SSH_keys` as a dict containing `instance_id: key_path`
