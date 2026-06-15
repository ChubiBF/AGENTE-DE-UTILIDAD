from roboflow import Roboflow
rf = Roboflow(api_key="OmGYJ9XIPBU3xtxJQaaE")
project = rf.workspace("baldiviezos-workspace-eo23t").project("my-first-project-qtnlw")
version = project.version(1)
dataset = version.download("yolov8")
