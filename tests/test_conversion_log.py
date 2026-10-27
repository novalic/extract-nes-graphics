"""Tests for extract_nes_graphics.conversion_log."""
from extract_nes_graphics.conversion_log import build_log_text, write_log


class TestBuildLogText:
    def test_includes_counts_and_dates(self):
        text = build_log_text(2, 1, '@@bad.chr', '10/14/17 - 14:33:17', '10/14/17 - 14:52:43')

        assert 'EXECUTION COMPLETE.' in text
        assert 'Started: 10/14/17 - 14:33:17' in text
        assert 'Finished: 10/14/17 - 14:52:43' in text
        assert 'Total files processed: 3' in text
        assert 'Successfully converted: 2' in text
        assert 'Not converted (ERROR): 1' in text
        assert 'bad.chr' in text

    def test_no_bad_files_still_produces_valid_text(self):
        text = build_log_text(5, 0, '', 'start', 'end')
        assert 'Total files processed: 5' in text
        assert 'Not converted (ERROR): 0' in text

    def test_multiple_bad_files_are_each_on_their_own_line(self):
        text = build_log_text(0, 2, '@@one.chr@@two.nes', 'start', 'end')
        lines = text.splitlines()
        assert 'one.chr' in lines
        assert 'two.nes' in lines


class TestWriteLog:
    def test_writes_log_txt_inside_dump_dir(self, tmp_path):
        write_log(str(tmp_path), 1, 1, '@@bad.chr', 'start', 'end')

        log_file = tmp_path / 'LOG.TXT'
        assert log_file.exists()
        content = log_file.read_text()
        assert 'Total files processed: 2' in content
        assert 'bad.chr' in content

    def test_overwrites_existing_log(self, tmp_path):
        log_file = tmp_path / 'LOG.TXT'
        log_file.write_text('stale content')

        write_log(str(tmp_path), 3, 0, '', 'start', 'end')

        assert 'stale content' not in log_file.read_text()
