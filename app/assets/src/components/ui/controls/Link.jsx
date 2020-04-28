import React from "react";
import PropTypes from "prop-types";
import cx from "classnames";

import { logAnalyticsEvent } from "~/api/analytics";
import cs from "./link.scss";

class Link extends React.Component {
  onClick = () => {
    const {
      analyticsEventData,
      analyticsEventName,
      external,
      href,
    } = this.props;

    if (analyticsEventName) {
      logAnalyticsEvent(analyticsEventName, analyticsEventData);
    } else {
      logAnalyticsEvent("Link_generic_clicked", {
        external: external,
        href: href,
      });
    }
  };

  render() {
    const { href, className, children, color, external } = this.props;
    return (
      <a
        href={href}
        className={cx(cs.link, className, color)}
        target={external ? "_blank" : null}
        rel="noopener noreferrer"
        onClick={this.onClick}
      >
        {children}
      </a>
    );
  }
}

Link.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string,
  external: PropTypes.bool,
  href: PropTypes.string,
  color: PropTypes.string,

  // We intentionally don't have an onClick prop, because we don't want to encourage arbitrary onClick handlers,
  // since there is already an on-click behavior (following the link href). logAnalyticsEvent is an exception.
  analyticsEventName: PropTypes.string,
  analyticsEventData: PropTypes.object,
};

Link.defaultProps = {
  analyticsEventData: {},
  externalLink: false,
  color: "primary-light",
};

export default Link;
