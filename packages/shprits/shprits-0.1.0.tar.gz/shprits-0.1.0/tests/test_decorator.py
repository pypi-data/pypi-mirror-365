from shprits.core.container import Container
from shprits.core.entities import Scope
from shprits.decorators import provide


def test_provide_decorator():
    class D(Container):
        @provide(scope=Scope.APP)
        def foo(self) -> int:
            return 1

    c = D()
    assert c.resolve_sync(int) == 1
