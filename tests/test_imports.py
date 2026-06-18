def test_import_app_module():
    import claude_monitor.app

    assert claude_monitor.app.MonitorWindow is not None
