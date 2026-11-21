using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class KaizenAndroidBuild
{
    public static void BuildAndroid()
    {
        var scenes = EditorBuildSettings.scenes
            .Where(scene => scene.enabled)
            .Select(scene => scene.path)
            .ToArray();

        if (scenes.Length == 0)
            throw new InvalidOperationException("No enabled scenes are configured in Build Settings.");

        EditorUserBuildSettings.SwitchActiveBuildTarget(
            BuildTargetGroup.Android, BuildTarget.Android);

        var options = new BuildPlayerOptions
        {
            scenes = scenes,
            locationPathName = "Build/Android/SvZ2-Kaizen.apk",
            target = BuildTarget.Android,
            options = BuildOptions.None
        };

        BuildReport report = BuildPipeline.BuildPlayer(options);
        if (report.summary.result != BuildResult.Succeeded)
            throw new Exception("Android build failed: " + report.summary.result +
                                " (" + report.summary.totalErrors + " errors).");
        Debug.Log("Android APK created: " + options.locationPathName);
    }
}
