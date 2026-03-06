from v2g_cps.protocol.puf import DeterministicPUF


def test_puf_recovery_matches_base_response() -> None:
    puf = DeterministicPUF(seed=b"seed" * 8, label=b"v2g-cps:test")
    challenge = b"challenge"
    helper = puf.helper_data(challenge, epoch=2)
    response = puf.base_response(challenge, epoch=2)
    recovered = puf.recover(challenge, helper, epoch=2)
    assert recovered == response


def test_puf_noise_changes_sample() -> None:
    puf = DeterministicPUF(seed=b"seed" * 8, label=b"v2g-cps:test")
    challenge = b"challenge"
    assert puf.sample(challenge, epoch=0, noisy=True) != puf.sample(challenge, epoch=0, noisy=False)

