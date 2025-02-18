def _gen_code(self):
    # Inject code
    string = "\n"
    string += "//BEGIN DECLARATION OF THE ROBOT '" + self.name + "'\n\n"

    string += "const object3d_base_" + self.name + "_list = [];\n\n"

    if not (self.list_object_3d_base is None):
        for i in range(len(self.list_object_3d_base)):
            string += self.list_object_3d_base[i].gen_code(self.name + "_obj_base_" + str(i))
            string += "object3d_base_" + self.name + "_list.push(object3d_" + self.name + "_obj_base_" + str(i) + ");\n"

        string += "\n"

    string += "const list_links_" + self.name + " = [];\n\n"

    for i in range(len(self.links)):
        string += self.links[i].gen_code(self.name)
        string += "list_links_" + self.name + ".push(link_" + str(i) + "_" + self.name + ");\n\n"

    string += "const htm_" + self.name + "_base_0 = new Matrix4(); \n"
    string += "htm_" + self.name + "_base_0.set(" \
              + str(self.htm_base_0[0,0]) + "," + str(self.htm_base_0[0,1]) + "," + str(
        self.htm_base_0[0,2]) + "," + str(
        self.htm_base_0[0,3]) + "," \
              + str(self.htm_base_0[1,0]) + "," + str(self.htm_base_0[1,1]) + "," + str(
        self.htm_base_0[1,2]) + "," + str(
        self.htm_base_0[1,3]) + "," \
              + str(self.htm_base_0[2,0]) + "," + str(self.htm_base_0[2,1]) + "," + str(
        self.htm_base_0[2,2]) + "," + str(
        self.htm_base_0[2,3]) + "," \
              + str(self.htm_base_0[3,0]) + "," + str(self.htm_base_0[3,1]) + "," + str(
        self.htm_base_0[3,2]) + "," + str(
        self.htm_base_0[3,3]) + ");\n"

    string += "const var_" + self.name + " = new Robot(object3d_base_" + self.name + "_list, list_links_" + self.name + "," + str(
        self._frames) + ", htm_" + self.name + "_base_0," +( "true" if self.eef_frame_visible else "false" )+");\n"
    string += "sceneElements.push(var_" + self.name + ");\n"
    string += "//USER INPUT GOES HERE"

    return string
