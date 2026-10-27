"""Builds and writes the LOG.TXT summary produced by a folder conversion."""


def build_log_text(num_good, num_bad, bad_files, date_start, date_end):
    """Render the LOG.TXT contents for a folder-conversion run.

    `bad_files` is the '@@'-joined string of failed file names accumulated
    by the batch converter (see batch.convert_folder).
    """
    lines = [
        'EXECUTION COMPLETE.',
        'Started: ' + date_start,
        'Finished: ' + date_end,
        '_' * 50,
        'Total files processed: ' + str(num_good + num_bad),
        'Successfully converted: ' + str(num_good),
        'Not converted (ERROR): ' + str(num_bad),
        '_' * 50,
    ]
    lines.extend(bad_files.split('@@'))
    lines.append('_' * 50)
    return '\n'.join(lines) + '\n'


def write_log(dump_dir, num_good, num_bad, bad_files, date_start, date_end):
    """Write LOG.TXT inside `dump_dir` with the summary of the run."""
    log_text = build_log_text(num_good, num_bad, bad_files, date_start, date_end)
    with open(dump_dir + '/LOG.TXT', 'w') as execution_log:
        execution_log.write(log_text)
