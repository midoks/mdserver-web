<?php
// Synchronous dispatcher: receive() blocks the thread, so the worker handles one request at a time.

use Rapira\Exception\ClosedException;
use Rapira\Exception\RapiraThrowable;
use Rapira\Http\Request;

final class PageNotFound extends \RuntimeException {}

function handle(Request $req): Generator | string {
	return match ($req->target) {
		'/'       => "hello from the sync dispatcher\n",
		'/echo'   => \is_string($req->body) ? $req->body : '',
		'/stream' => generateStream(),
		'/boom'   => throw new \RuntimeException('the handler blew up'),
		default   => throw new PageNotFound("no route for {$req->target}"),
	};
}

function generateStream(): Generator {
	$j = mt_rand(5, 20);
	for ($i = 0; $i < $j; $i++) {
		yield "stream chunk {$i}\n";
	}

	return "stream done\n";
}

$d = \Rapira\get_dispatcher();

while (true) {
	try {
		while (true) {
			$ex = $d->receive();

			$body = handle($ex->getRequest());
			$ex->writeHead(200, ['content-type' => ['text/plain']]);
			if ($body instanceof Generator) {
				foreach ($body as $chunk) {
					$ex->writeBody($chunk, eos: false);
				}

				$ex->writeBody($body->getReturn());
			} else {
				$ex->writeBody($body);
			}
		}
	} catch (PageNotFound $e) {
		try {
			$ex->writeHead(404, ['content-type' => ['text/plain']]);
			$ex->writeBody("not found: {$e->getMessage()}\n");
		} catch (\Throwable) {
		}
	} catch (ClosedException) {
		// Drained: no more work will ever arrive.
		break;
	} catch (RapiraThrowable) {
		// The http plugin closed the exchange first - nothing to answer, move on.
	} catch (\Throwable $e) {
		try {
			$ex->writeHead(500, ['content-type' => ['text/plain']]);
			$ex->writeBody("internal error: {$e->getMessage()}\n");
		} catch (\Throwable) {
		}
	}
}