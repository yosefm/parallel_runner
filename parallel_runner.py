# Provides a base class for running several jobs in parallel, controlling them
# while they run, etc.

from multiprocessing import Process

class PoolWorker(Process):
	"""
	A class for a process that is part of a scatter pool, where jobs are given
	to pool workers through a shared queue, and commands for suspending/
	resuming/ending execution in a worker can be sent to workers through a
	separate channel.
	
	To use the class, subclass it and override job() and maybe pre_run()
	"""
	def __init__(self, tasks, command_pipe, results_queue=None):
		self._t = tasks
		self._out_q = results_queue
		self._cmd = command_pipe
		Process.__init__(self)
	
	def run(self):
		self.pre_run()
		while not self._t.empty():
			# Before each simulation, check for orders from the central process
			if self._cmd.poll():
				cmd = self._cmd.recv()
				if cmd == "end":
					return
			
			res = self.job(self._t.get())
			if self._out_q is not None:
				self._out_q.put(res)
				del res # Allow returning huge results.
	
	def pre_run(self):
		"""Override to do something before the jobs-loop starts"""
		pass
	
	def job(self, prm):
		"""
		Override to do the job whose parameters are in prm, as taken from the
		jobs queue.
		"""
		pass
