import os, re, sys, argparse
import unreal
 
class UnrealImportTask:
    def __init__(self):
        self.editorAssetLib = unreal.EditorAssetLibrary()
        self.stringLib = unreal.StringLibrary()
 
    def executeImportTasks(self, tasks):
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
            for task in tasks:
                for path in task.get_editor_property('imported_object_paths'):
                    print
                    'Imported: %s' % path
 
    def buildStaticMeshImportOptions(self):
        fbxOptions = unreal.FbxImportUI()
        static_mesh_import_data = unreal.FbxStaticMeshImportData()
        static_mesh_import_data.set_editor_property('combine_meshes', True)
        fbxOptions.set_editor_property('import_mesh', True)
        fbxOptions.set_editor_property('import_textures', False)
        fbxOptions.set_editor_property('import_materials', True)
        fbxOptions.set_editor_property('import_as_skeletal', False)
        fbxOptions.set_editor_property('static_mesh_import_data', static_mesh_import_data)
        return fbxOptions
 
    def buildImportTask(self, filename, destination_path, options=None):
        task = unreal.AssetImportTask()
        task.set_editor_property('automated', True)
        task.set_editor_property('destination_name', '')
        task.set_editor_property('destination_path', destination_path)
        task.set_editor_property('filename', filename)
        task.set_editor_property('replace_existing', True)
        task.set_editor_property('save', False)
        task.set_editor_property('options', options)
        return task
    def importStaticMesh(self, meshFilePath, destination_path):
        taskList = []
        taskList.append(self.buildImportTask(meshFilePath, destination_path, self.buildStaticMeshImportOptions()))
        self.executeImportTasks(taskList)
    
    def separateMaterials(self, destination_path):
        allAssets = self.editorAssetLib.list_assets(destination_path, True, False)
        for asset in allAssets:
            _assetData = self.editorAssetLib.find_asset_data(asset)
            _assetClassName = _assetData.get_asset().get_class().get_name()
 
            if _assetClassName == "Material":
                _assetName = _assetData.get_asset().get_name()
                _assetPathName = _assetData.get_asset()
                mat = self.editorAssetLib.load_asset(asset)
                mat.set_editor_property("two_sided", True)
                _targetPathName = "{}Materials/{}".format(destination_path, _assetName)
                self.editorAssetLib.rename_loaded_asset(_assetPathName, _targetPathName)
    
    def importTexures(self, texFilePath, destination_path):
        texImportTasks = []
        files = [f for f in os.listdir(texFilePath) if os.path.isfile(os.path.join(texFilePath, f)) and f[-3:]=='tga']
        AssetTools = unreal.AssetToolsHelpers.get_asset_tools()
        for f in files:
            texImportTask = unreal.AssetImportTask()
            texImportTask.set_editor_property('filename', os.path.join(texFilePath, f))
            texImportTask.set_editor_property('destination_path', destination_path)
            texImportTask.set_editor_property('save', False)
            texImportTasks.append(texImportTask)
        AssetTools.import_asset_tasks(texImportTasks)
 
    def textureParamEdit(self, destination_path):
        texurePath = destination_path
        textureAssets = self.editorAssetLib.list_assets(texurePath)
        for textureAsset in textureAssets:
            if self.stringLib.contains(textureAsset, "NORM"):
                texture = self.editorAssetLib.load_asset(textureAsset)
                texture.set_editor_property("sRGB", False)
                texture.set_editor_property("CompressionSettings", unreal.TextureCompressionSettings.TC_NORMALMAP)
                self.editorAssetLib.save_loaded_asset(texture)
 
            if self.stringLib.contains(textureAsset, "SPECR"):
                texture = self.editorAssetLib.load_asset(textureAsset)
                texture.set_editor_property("sRGB", False)
                texture.set_editor_property("CompressionSettings", unreal.TextureCompressionSettings.TC_MASKS)
                self.editorAssetLib.save_loaded_asset(texture)
 
            if self.stringLib.contains(textureAsset, "AO"):
                texture = self.editorAssetLib.load_asset(textureAsset)
                texture.set_editor_property("sRGB", False)
                texture.set_editor_property("CompressionSettings", unreal.TextureCompressionSettings.TC_MASKS)
                self.editorAssetLib.save_loaded_asset(texture)
 
def getFilePath(dirName, assetPath):
    if os.listdir(assetPath):
        versionList = (os.listdir(assetPath + dirName + "/"))
        if versionList:
            versionList.sort()
            latestVersion = versionList[-1]
            filePathText = assetPath + "{}/{}/".format(dirName, latestVersion)
    else:
        pass
    return filePathText
 
def getArguments(args):
    parser = argparse.ArgumentParser(description="Import StaticMesh")
    parser.add_argument("assetPath", nargs = "?", type = str, help = "Gives the mesh path")
    parser.add_argument("importType", nargs = "?", type = str, help = "Gives the dir name from Unreal")
    return vars(parser.parse_args(args))

def main():
    args = getArguments(sys.argv[1:])
    assetPath = args["assetPath"] + "/"
    importType = args["importType"]
    dirName = importType
    filePath = getFilePath(dirName, assetPath)
    destination_path = filePath.replace("/jobs/library/texture/textureLibrary/Artists/siva-n/unreal/CodeProjTest/Content", "/Game")
    unrealImport = UnrealImportTask()
    if importType == "Model":
        unrealImport.importStaticMesh(filePath, destination_path)
        unrealImport.separateMaterials(destination_path)
    elif importType == "Textures":
        unrealImport.importTexures(filePath, destination_path)
        unrealImport.textureParamEdit(destination_path)
main()