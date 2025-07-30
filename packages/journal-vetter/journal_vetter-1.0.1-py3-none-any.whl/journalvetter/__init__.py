from .core import do_vet_journals

__all__ = ["vet_journals"]

def vet_journals(*, 
                 cfg, 
                 config_file_path, 
                 resources_path, 
                 output_file=None,
                 field=None, 
                 impact_factor=None, 
                 cell_line=None, 
                 model_type=None):
    """
    Library‑style entrypoint. 
    Always returns just the title(s) (mode defaults to 'library').
    """
    return do_vet_journals(
        cfg,
        config_file_path,
        resources_path,
        output_file or resources_path,   # output_file is ignored in library mode
        field,
        impact_factor,
        cell_line,
        model_type,
        mode="library",
    )
