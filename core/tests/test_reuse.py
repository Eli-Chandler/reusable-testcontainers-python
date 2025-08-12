import time

import docker.errors
import pytest

from testcontainers.core.container import DockerContainer


def test_container_reuse():
    container1 = DockerContainer("busybox:latest", reuse=True)
    container1.start()
    container2 = DockerContainer("busybox:latest", reuse=True)
    container2.start()

    assert container1._container is not None
    assert container2._container is not None

    assert container1._container.id == container2._container.id

    container3 = DockerContainer("busybox:latest", reuse=False)
    container3.start()

    assert container3._container is not None

    assert container3._container.id != container1._container.id
    assert container3._container.id != container2._container.id

    container1.stop()
    with pytest.raises(docker.errors.NotFound):
        # I'm not 100% sure how I want to handle this
        # The intended use of `reuse` is really to re-use containers between test runs
        # Not within the same run
        # So you wouldn't expect to stop a container that isn't actually running
        # Stop shouldn't really be called at all when reuse=True
        container2.stop()
    container3.stop()


def test_container_reuse_with_keys():
    container_same_key_1 = DockerContainer("busybox:latest", reuse=True, reuse_key="mykey")
    container_same_key_2 = DockerContainer("busybox:latest", reuse=True, reuse_key="mykey")
    container_different_key = DockerContainer("busybox:latest", reuse=True, reuse_key="differentkey")
    container_no_key = DockerContainer("busybox:latest", reuse=True)

    container_same_key_1.start()
    container_same_key_2.start()
    container_different_key.start()
    container_no_key.start()

    assert container_same_key_1._container is not None
    assert container_same_key_2._container is not None
    assert container_different_key._container is not None
    assert container_no_key._container is not None

    assert container_same_key_1._container.id == container_same_key_2._container.id

    assert container_same_key_1._container.id != container_different_key._container.id
    assert container_same_key_2._container.id != container_different_key._container.id

    assert container_same_key_1._container.id != container_no_key._container.id
    assert container_same_key_2._container.id != container_no_key._container.id

    assert container_different_key._container.id != container_same_key_1._container.id

    container_same_key_1.stop()
    with pytest.raises(docker.errors.NotFound):
        container_same_key_2.stop()
    container_different_key.stop()
    container_no_key.stop()
