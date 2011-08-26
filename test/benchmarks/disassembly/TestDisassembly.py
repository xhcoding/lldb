"""Disassemble lldb's Driver::MainLoop() functions comparing lldb against gdb."""

import os, sys
import unittest2
import lldb
import pexpect
from lldbbench import *

class DisassembleDriverMainLoop(BenchBase):

    mydir = os.path.join("benchmarks", "example")

    def setUp(self):
        BenchBase.setUp(self)
        self.exe = self.lldbHere
        self.function = 'Driver::MainLoop()'
        self.lldb_avg = None
        self.gdb_avg = None

    @benchmarks_test
    def test_run_lldb_then_gdb(self):
        """Test disassembly on a large function with lldb vs. gdb."""
        print
        self.run_lldb_disassembly(self.exe, self.function, 5)
        print "lldb benchmark:", self.stopwatch
        self.run_gdb_disassembly(self.exe, self.function, 5)
        print "gdb benchmark:", self.stopwatch
        print "lldb_avg/gdb_avg: %f" % (self.lldb_avg/self.gdb_avg)

    @benchmarks_test
    def test_run_gdb_then_lldb(self):
        """Test disassembly on a large function with lldb vs. gdb."""
        print
        self.run_gdb_disassembly(self.exe, self.function, 5)
        print "gdb benchmark:", self.stopwatch
        self.run_lldb_disassembly(self.exe, self.function, 5)
        print "lldb benchmark:", self.stopwatch
        print "lldb_avg/gdb_avg: %f" % (self.lldb_avg/self.gdb_avg)

    def run_lldb_disassembly(self, exe, function, count):
        # Set self.child_prompt, which is "(lldb) ".
        self.child_prompt = '(lldb) '
        prompt = self.child_prompt

        # So that the child gets torn down after the test.
        self.child = pexpect.spawn('%s %s' % (self.lldbExec, exe))
        child = self.child

        # Turn on logging for what the child sends back.
        if self.TraceOn():
            child.logfile_read = sys.stdout

        child.expect_exact(prompt)
        child.sendline('breakpoint set -F %s' % function)
        child.expect_exact(prompt)
        child.sendline('run')
        child.expect_exact(prompt)

        # Reset the stopwatch now.
        self.stopwatch.reset()
        for i in range(count):
            with self.stopwatch:
                # Disassemble the function.
                child.sendline('disassemble -f')
                child.expect_exact(prompt)
            child.sendline('next')
            child.expect_exact(prompt)

        child.sendline('quit')
        try:
            self.child.expect(pexpect.EOF)
        except:
            pass

        self.lldb_avg = self.stopwatch.avg()
        if self.TraceOn():
            print "lldb disassembly benchmark:", str(self.stopwatch)
        self.child = None

    def run_gdb_disassembly(self, exe, function, count):
        # Set self.child_prompt, which is "(gdb) ".
        self.child_prompt = '(gdb) '
        prompt = self.child_prompt

        # So that the child gets torn down after the test.
        self.child = pexpect.spawn('gdb %s' % exe)
        child = self.child

        # Turn on logging for what the child sends back.
        if self.TraceOn():
            child.logfile_read = sys.stdout

        child.expect_exact(prompt)
        child.sendline('break %s' % function)
        child.expect_exact(prompt)
        child.sendline('run')
        child.expect_exact(prompt)

        # Reset the stopwatch now.
        self.stopwatch.reset()
        for i in range(count):
            with self.stopwatch:
                # Disassemble the function.
                child.sendline('disassemble')
                child.expect_exact(prompt)
            child.sendline('next')
            child.expect_exact(prompt)

        child.sendline('quit')
        child.expect_exact('The program is running.  Exit anyway?')
        child.sendline('y')
        try:
            self.child.expect(pexpect.EOF)
        except:
            pass

        self.gdb_avg = self.stopwatch.avg()
        if self.TraceOn():
            print "gdb disassembly benchmark:", str(self.stopwatch)
        self.child = None


if __name__ == '__main__':
    import atexit
    lldb.SBDebugger.Initialize()
    atexit.register(lambda: lldb.SBDebugger.Terminate())
    unittest2.main()
